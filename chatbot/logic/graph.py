"""
GraphAgent: LangGraph-based conversational agent with tool usage.

This module implements the main agent logic using LangGraph for orchestrating
conversation flows. The agent can:

- Answer questions using RAG (Retrieval-Augmented Generation)
- Consult teaching guides stored in MongoDB
- Search the web for additional information
- Generate and manage interactive test sessions
- Maintain conversation state using SQLite checkpointing

Architecture:
    The agent uses a StateGraph with multiple nodes:

    1. **think**: Main reasoning node that decides actions
    2. **rag_search**: Semantic search in document database
    3. **get_guia**: Retrieve teaching guide information
    4. **test_session**: Test generation and management subgraph

    Flow:
        User Query -> think -> [tool_node] -> think -> Response
                              ↓
                        test_session (if test mode)
                              ↓
                        interrupt with questions
                              ↓
                        resume with answers

Key Features:
    - **Multi-LLM Support**: Configurable vLLM or Gemini chatbot
    - **Persistent State**: SQLite checkpointer for conversation continuity
    - **Tool Calling**: Automatic tool selection and execution
    - **Test Mode**: Interactive test sessions with interrupts
    - **Context Management**: Maintains relevant document snippets

Example:
    # Initialize agent
    agent = GraphAgent(llm_provider="gemini")

    # Chat
    response = agent.call_agent(
        query="¿Qué es Docker?",
        id="session_123",
        asignatura="iv"
    )

    # Resume test
    response = agent.call_agent_resume(
        id="session_123",
        resume_value="B"
    )
"""

import logging
import os
import sqlite3
from typing import Any, Literal

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mistralai import ChatMistralAI
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, MessagesState, StateGraph

from chatbot.config import settings
from chatbot.logic.prompts import SYSTEM_PROMPT_COT, SYSTEM_PROMPT_V3
from chatbot.logic.query_classifier import QueryComplexity, classify_query
from chatbot.logic.tools.tools import get_tools

logger = logging.getLogger(__name__)


class SubjectState(MessagesState):
    """
    State schema for the conversational agent graph.

    Extends LangGraph's MessagesState to include additional fields for:
    - Subject/course context (asignatura)
    - Retrieved document snippets (context)
    - Test session management fields

    Attributes:
        messages: List of conversation messages (inherited from MessagesState)
        asignatura: Current subject/course being discussed
        context: Document snippets retrieved by RAG tools

        Test session fields (only populated during test mode):
            topic: Test topic/theme
            num_questions: Number of questions in the test
            difficulty: Difficulty level (easy/medium/hard)
            questions: List of generated questions
            current_question_index: Index of current question being asked
            user_answers: List of user's answers
            feedback_history: Feedback for each answer
            scores: Boolean list indicating correct/incorrect answers
    """

    asignatura: str | None
    # `context` will hold a list of document snippets returned by RAG tools
    context: list[dict[str, Any]] | None
    # Chain-of-Thought reasoning from last response (if CoT was used)
    thinking: str | None

    # Test session fields (shared with test subgraph)
    topic: str | None
    num_questions: int | None
    difficulty: str | None
    questions: list[Any] | None  # List[MultipleChoiceTest]
    current_question_index: int | None
    user_answers: list[str] | None
    feedback_history: list[str] | None
    scores: list[bool] | None
    pending_feedback: str | None


class GraphAgent:
    """
    Conversational agent powered by LangGraph and LLMs.

    This class encapsulates the entire agent logic including graph construction,
    tool integration, and conversation management. It supports multiple LLM
    providers (vLLM, Gemini) and maintains conversation state using SQLite.

    The agent orchestrates complex conversational flows including:
    - Multi-turn conversations with context retention
    - Tool calling for information retrieval
    - Test generation and interactive assessment
    - Interrupt/resume flow for user input collection

    Design Decisions:
        - Single instance per application to share checkpointer
        - Lazy graph compilation (compiled on first use)
        - SQLite for persistent conversation state
        - Configurable LLM chatbot for flexibility
    """

    def __init__(
        self,
        *,
        llm_provider: Literal["vllm", "gemini", "mistral"] = "vllm",
        vllm_port: str | None = None,
        model_dir: str | None = None,
        openai_api_key: str = "EMPTY",
        gemini_api_key: str | None = None,
        gemini_model: str | None = None,
        mistral_api_key: str | None = None,
        mistral_model: str | None = None,
        temperature: float = 0.1,
    ):
        """Initialize GraphAgent with configurable LLM provider.

        Args:
            llm_provider: "vllm" (local), "gemini" (Google), or "mistral" (Mistral AI)
            vllm_port: Port for vLLM service (only for vllm provider)
            model_dir: Model directory (only for vllm provider)
            openai_api_key: API key for vLLM OpenAI-compatible endpoint
            gemini_api_key: Google Gemini API key (only for gemini provider)
            gemini_model: Gemini model name (default: gemini-2.5-flash)
            mistral_api_key: Mistral AI API key (only for mistral provider)
            mistral_model: Mistral model name (default: mistral-large-latest)
            temperature: LLM temperature
        """
        self.llm_provider = llm_provider
        self.temperature = temperature

        # vLLM configuration (use settings, allow parameter override)
        self.vllm_url = settings.vllm_url
        self.model_name = model_dir or settings.model_path
        self.openai_api_key = openai_api_key

        # Gemini configuration
        self.gemini_api_key = gemini_api_key or settings.get_gemini_api_key()
        self.gemini_model = gemini_model or settings.gemini_model
        if self.gemini_api_key:
            os.environ["GOOGLE_API_KEY"] = self.gemini_api_key

        # Mistral configuration
        self.mistral_api_key = mistral_api_key or settings.get_mistral_api_key()
        self.mistral_model = mistral_model or settings.mistral_model

        # Cache interno del grafo compilado
        self._graph = None

    def _get_llm(self, temperature: float | None = None):
        """Get configured LLM instance based on provider.

        Args:
            temperature: Override temperature (uses instance default if None)

        Returns:
            Configured LLM instance (ChatOpenAI, ChatGoogleGenerativeAI, or ChatMistralAI)
        """
        temp = temperature if temperature is not None else self.temperature

        if self.llm_provider == "gemini":
            if not self.gemini_api_key:
                raise ValueError(
                    "GEMINI_API_KEY not found. Set it in .env or pass gemini_api_key parameter."
                )
            return ChatGoogleGenerativeAI(
                model=self.gemini_model,
                google_api_key=self.gemini_api_key,
                temperature=temp,
            )
        elif self.llm_provider == "mistral":
            if not self.mistral_api_key:
                raise ValueError(
                    "MISTRAL_API_KEY not found. Set it in .env or pass mistral_api_key parameter."
                )
            return ChatMistralAI(
                model=self.mistral_model,
                mistral_api_key=self.mistral_api_key,
                temperature=temp,
            )
        else:  # vllm
            return ChatOpenAI(
                model=self.model_name,
                openai_api_key=self.openai_api_key,
                openai_api_base=self.vllm_url,
                temperature=temp,
            )

    def think(self, state: SubjectState):
        """
        Main reasoning node of the agent with adaptive Chain-of-Thought.

        This node is the brain of the agent. It receives the conversation state,
        classifies the query complexity, and decides whether to:
        - Use simple prompt for straightforward queries (lower latency)
        - Use CoT prompt for complex queries (better reasoning)

        The LLM is bound with tools, enabling automatic tool selection based on
        the query content and conversation context.

        Args:
            state: Current conversation state with messages and context

        Returns:
            Dict with updated messages and optional thinking field
        """
        import re

        tools = get_tools()
        asignatura = state.get("asignatura") or "general"
        messages = state["messages"]

        # Get the last user message for classification
        last_user_message = None
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                last_user_message = msg.content
                break

        # Classify query complexity
        use_cot = False
        if last_user_message:
            complexity = classify_query(last_user_message)
            use_cot = complexity == QueryComplexity.COMPLEX
            logger.debug(
                f"Query classified as {complexity.value}: '{last_user_message[:50]}...'"
            )

        # Select appropriate prompt based on complexity
        if use_cot:
            system_prompt = SYSTEM_PROMPT_COT.format(asignatura=asignatura)
        else:
            system_prompt = SYSTEM_PROMPT_V3.format(asignatura=asignatura)

        system_message = SystemMessage(content=system_prompt)

        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [system_message] + messages

        llm = self._get_llm().bind_tools(tools)
        response = llm.invoke(messages)

        # Parse CoT response if applicable
        result: dict[str, Any] = {"messages": [response]}

        if use_cot and hasattr(response, "content") and response.content:
            content = response.content

            # Extract thinking section
            thinking_match = re.search(
                r"<thinking>(.*?)</thinking>", content, re.DOTALL
            )
            if thinking_match:
                result["thinking"] = thinking_match.group(1).strip()
                logger.debug(f"Extracted thinking: {result['thinking'][:100]}...")

            # Extract answer section and update response content
            answer_match = re.search(r"<answer>(.*?)</answer>", content, re.DOTALL)
            if answer_match:
                # Update the response content to only show the answer
                from langchain_core.messages import AIMessage

                clean_answer = answer_match.group(1).strip()
                result["messages"] = [
                    AIMessage(
                        content=clean_answer,
                        tool_calls=getattr(response, "tool_calls", []),
                    )
                ]

        return result

    def rag_search(self, state: SubjectState):
        """
        RAG search node - semantic search over document database.

        Executes the rag_search tool to find relevant document chunks based on
        the user's query. Results are stored in the state's context field and
        returned as a ToolMessage for the agent to process.

        Args:
            state: Current conversation state

        Returns:
            Dict with ToolMessage containing search results
        """
        tools = get_tools()
        rag_tool = next((tool for tool in tools if tool.name == "rag_search"), None)

        if rag_tool is None:
            raise ValueError("RAG search tool not found")

        messages = state["messages"]
        last_message = messages[-1]

        tool_calls = getattr(last_message, "tool_calls", [])
        if not tool_calls:
            # No hay llamadas a herramientas, no hacer nada
            return {"context": []}

        tool_messages = []

        for tc in tool_calls:
            if tc["name"] == "rag_search":
                tool_call_id = tc["id"]
                args = tc["args"]

                # Execute tool
                rag_result = rag_tool.invoke(args)
                results = rag_result.get("results", [])

                content = "This is chunks of context:\n"
                for result in results:
                    content += f"\n- {result['content']}\n"
                    # Store both content and metadata
                    if state.get("context") is None:
                        state["context"] = []
                    state["context"].append(
                        {"content": result["content"], "metadata": result["metadata"]}
                    )
                tool_messages.append(
                    ToolMessage(content=content, tool_call_id=tool_call_id)
                )
            else:
                # Placeholder response for other tool calls to satisfy Mistral
                tool_messages.append(
                    ToolMessage(
                        content="Procesando...",
                        tool_call_id=tc["id"],
                    )
                )

        return {"messages": tool_messages}

    def get_guia(self, state: SubjectState):
        """
        Teaching guide retrieval node.

        Fetches structured information from the teaching guide (guía docente)
        stored in MongoDB for the current subject. This provides quick access
        to course details, competencies, evaluation criteria, etc.

        Args:
            state: Current conversation state (must include asignatura)

        Returns:
            Dict with ToolMessage containing teaching guide information
        """
        tools = get_tools()
        guia_tool = next((tool for tool in tools if tool.name == "get_guia"), None)

        if guia_tool is None:
            raise ValueError("Get Guia tool not found")

        messages = state["messages"]
        last_message = messages[-1]

        tool_calls = getattr(last_message, "tool_calls", [])
        if not tool_calls:
            # No hay llamadas a herramientas, no hacer nada
            return state

        tool_messages = []
        for tc in tool_calls:
            if tc["name"] == "get_guia":
                tool_call_id = tc["id"]
                args = tc["args"]
                args["asignatura"] = state.get("asignatura")

                content = guia_tool.invoke(args)
                tool_messages.append(
                    ToolMessage(content=content, tool_call_id=tool_call_id)
                )
            else:
                tool_messages.append(
                    ToolMessage(
                        content="Procesando...",
                        tool_call_id=tc["id"],
                    )
                )

        return {"messages": tool_messages}

    def should_continue(self, state: SubjectState):
        """Decide si el agente debe continuar o terminar."""
        messages = state["messages"]
        last_message = messages[-1]

        # Si el último mensaje tiene tool_calls, continuar a las herramientas
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return last_message.tool_calls[0]["name"]
        else:
            return END

    def build_graph(self):
        """Construye y compila el grafo del agente y lo cachea en self._graph."""
        from chatbot.logic.testGraph import create_test_subgraph

        # Use the SubjectState so tools can inject 'asignatura' into tool args
        graph_builder = StateGraph(SubjectState)

        # Build test subgraph (will be added as a node)
        # Pass LLM configuration to test subgraph
        test_subgraph = create_test_subgraph(
            llm_provider=self.llm_provider,
            vllm_url=self.vllm_url,
            model_name=self.model_name,
            openai_api_key=self.openai_api_key,
            gemini_api_key=self.gemini_api_key,
            gemini_model=self.gemini_model,
            mistral_api_key=self.mistral_api_key,
            mistral_model=self.mistral_model,
            temperature=0.7,  # Higher temperature for test evaluation
        )

        # Agregar nodos
        graph_builder.add_node("agent", self.think)
        graph_builder.add_node("rag_search", self.rag_search)
        graph_builder.add_node("get_guia", self.get_guia)
        # Add test subgraph DIRECTLY as a node (not invoked!)
        graph_builder.add_node("test_session", test_subgraph)

        # Definir el punto de entrada
        graph_builder.set_entry_point("agent")

        # Agregar aristas
        graph_builder.add_conditional_edges(
            "agent",
            self.should_continue,
            {
                "rag_search": "rag_search",
                "get_guia": "get_guia",
                "generate_test": "test_session",  # Route to subgraph node!
                END: END,
            },
        )
        graph_builder.add_edge("rag_search", "agent")
        graph_builder.add_edge("get_guia", "agent")
        graph_builder.add_edge("test_session", END)  # Finalize after test session

        # Preparar persistencia
        storage_dir = os.path.join(os.path.dirname(__file__), "..", "storage")
        os.makedirs(storage_dir, exist_ok=True)
        checkpoint_path = os.path.join(storage_dir, "checkpoints.db")
        conn = sqlite3.connect(checkpoint_path, check_same_thread=False)
        memory = SqliteSaver(conn)

        self._graph = graph_builder.compile(checkpointer=memory)
        return self._graph

    def call_agent(self, query: str, id: str, asignatura: str | None = None):
        """Llama al agente compilado con una consulta sencilla.

        Args:
            query: texto de la consulta del usuario
            id: identificador (por ahora se usa como thread_id en la configuración)

        Returns:
            El resultado de invocar el grafo compilado (dict con 'messages').
        """
        # Compilar grafo si es necesario
        if self._graph is None:
            self.build_graph()

        if self._graph is None:
            raise ValueError("Failed to build graph")

        state = {
            "messages": [HumanMessage(content=query)],
            "asignatura": asignatura,
            "context": [],
        }
        config = {"configurable": {"thread_id": id, "asignatura": asignatura}}

        return self._graph.invoke(state, config=config)

    def call_agent_resume(self, id: str, resume_value: str):
        """Resume an interrupted graph execution.

        Args:
            id: thread_id of the interrupted conversation
            resume_value: the user's response (answer to question)

        Returns:
            The result of resuming the graph execution
        """
        from langgraph.types import Command

        if self._graph is None:
            self.build_graph()

        if self._graph is None:
            raise ValueError("Failed to build graph")

        config = {"configurable": {"thread_id": id}}

        # Resume using Command with the user's answer
        return self._graph.invoke(Command(resume=resume_value), config=config)

    def get_history(self, id: str) -> list:
        """Get conversation history for a session.

        Args:
            id: thread_id of the conversation

        Returns:
            List of messages from the conversation state
        """
        if self._graph is None:
            self.build_graph()

        if self._graph is None:
            raise ValueError("Failed to build graph")

        config = {"configurable": {"thread_id": id}}

        try:
            state = self._graph.get_state(config)
            if state and state.values:
                return state.values.get("messages", [])
            return []
        except Exception as e:
            logger.warning(f"Could not retrieve history for thread {id}: {e}")
            return []
