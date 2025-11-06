"""Clase que encapsula la construcción del grafo y la llamada al agente."""

import os
import logging
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, ToolMessage, HumanMessage
from langgraph.graph import StateGraph, END, MessagesState
from typing import TypedDict, Optional, List, Dict, Any, Literal
from langgraph.types import interrupt

logger = logging.getLogger(__name__)

class SubjectState(MessagesState):
    """Graph state that includes conversation messages, selected asignatura
    and a retrieval `context` where tool nodes can store document snippets.
    
    Also includes test session fields (shared with test subgraph).
    These are only populated when in test mode.
    """
    asignatura: Optional[str]
    # `context` will hold a list of document snippets returned by RAG tools
    context: Optional[List[Dict[str, Any]]]
    
    # Test session fields (shared with test subgraph)
    topic: Optional[str]
    num_questions: Optional[int]
    difficulty: Optional[str]
    questions: Optional[List[Any]]  # List[MultipleChoiceTest]
    current_question_index: Optional[int]
    user_answers: Optional[List[str]]
    feedback_history: Optional[List[str]]
    scores: Optional[List[bool]]

from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.sqlite import SqliteSaver

from backend.logic.tools.tools import get_tools
from backend.logic.prompts import SYSTEM_PROMPT_V1, SYSTEM_PROMPT_V2

import sqlite3

# --- CONFIGURACIÓN ---
load_dotenv()


class GraphAgent:
    """Clase que encapsula la construcción del grafo y la llamada al agente."""

    def __init__(
        self, 
        *, 
        llm_provider: Literal["vllm", "gemini"] = "vllm",
        vllm_port: str | None = None, 
        model_dir: str | None = None,
        openai_api_key: str = "EMPTY", 
        gemini_api_key: str | None = None,
        gemini_model: str = "gemini-2.0-flash",
        temperature: float = 0.1
    ):
        """Initialize GraphAgent with configurable LLM provider.
        
        Args:
            llm_provider: Either "vllm" (local vLLM) or "gemini" (Google Gemini)
            vllm_port: Port for vLLM service (only for vllm provider)
            model_dir: Model directory (only for vllm provider)
            openai_api_key: API key for vLLM OpenAI-compatible endpoint
            gemini_api_key: Google Gemini API key (only for gemini provider)
            gemini_model: Gemini model name (default: gemini-1.5-flash)
            temperature: LLM temperature
        """
        self.llm_provider = llm_provider
        self.temperature = temperature

        # vLLM configuration
        vllm_port = vllm_port or os.getenv("VLLM_MAIN_PORT", "8000")
        vllm_host = os.getenv("VLLM_HOST", "vllm-openai")
        self.vllm_url = f"http://{vllm_host}:{vllm_port}/v1"
        self.model_name = model_dir or os.getenv(
            "MODEL_PATH", "/models/HuggingFaceTB--SmolLM2-1.7B-Instruct"
        )
        self.openai_api_key = openai_api_key

        # Gemini configuration
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        self.gemini_model = gemini_model
        os.environ["GOOGLE_API_KEY"] = self.gemini_api_key


        # Cache interno del grafo compilado
        self._graph = None

    def _get_llm(self, temperature: float | None = None):
        """Get configured LLM instance based on provider.
        
        Args:
            temperature: Override temperature (uses instance default if None)
            
        Returns:
            Configured LLM instance (ChatOpenAI or ChatGoogleGenerativeAI)
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
        else:  # vllm
            return ChatOpenAI(
                model=self.model_name,
                openai_api_key=self.openai_api_key,
                openai_api_base=self.vllm_url,
                temperature=temp,
            )

    def think(self, state: SubjectState):
        """Nodo del Agente. Contesta a la pregunta dada o decide usar herramientas."""
        tools = get_tools()
        system_message = SystemMessage(content=SYSTEM_PROMPT_V2)

        messages = state["messages"]
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [system_message] + messages

        llm = self._get_llm().bind_tools(tools)

        response = llm.invoke(messages)

        return {"messages": [response]}
    
    def rag_search(self, state: SubjectState):
        """Nodo de búsqueda RAG. Realiza una búsqueda semántica y almacena los snippets en el estado."""
        tools = get_tools()
        rag_tool = next((tool for tool in tools if tool.name == "rag_search"), None)

        if rag_tool is None:
            raise ValueError("RAG search tool not found")

        messages = state["messages"]
        last_message = messages[-1]

        tool_calls = getattr(last_message, "tool_calls", [])
        if not tool_calls:
            # No hay llamadas a herramientas, no hacer nada
            state.context = []
            return state

        args = tool_calls[0]["args"]
        tool_call_id = tool_calls[0]["id"]

        rag_result = rag_tool.invoke(args)

        results = rag_result.get("results", [])

        content = "This is chunks of context:\n"
        
        for result in results:
            content += f"\n- {result["content"]}\n"
            state["context"].append(result["metadata"])


        tool_message = ToolMessage(
            content=content,
            tool_call_id=tool_call_id 
        )

        return {"messages": [tool_message]}
    
    def get_guia(self, state: SubjectState):
        """Nodo de obtención de guía. Recupera información de la guía y la añade al estado."""
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

        args = tool_calls[0]["args"]
        args["asignatura"] = state.get("asignatura")
        
        tool_call_id = tool_calls[0]["id"]

        guia_result = guia_tool.invoke(args)

        tool_message = ToolMessage(
            content=guia_result,
            tool_call_id=tool_call_id 
        )

        return {"messages": [tool_message]}
    
    def web_search(self, state: SubjectState):
        """Nodo de búsqueda web. Realiza una búsqueda web y añade los resultados al estado."""
        tools = get_tools()
        web_search_tool = next((tool for tool in tools if tool.name == "web_search"), None)

        if web_search_tool is None:
            raise ValueError("Web Search tool not found")

        messages = state["messages"]
        last_message = messages[-1]

        tool_calls = getattr(last_message, "tool_calls", [])
        if not tool_calls:
            # No hay llamadas a herramientas, no hacer nada
            return state

        args = tool_calls[0]["args"]
        tool_call_id = tool_calls[0]["id"]

        web_search_result = web_search_tool.invoke(args)

        tool_message = ToolMessage(
            content=web_search_result,
            tool_call_id=tool_call_id 
        )

        return {"messages": [tool_message]}

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
        from backend.logic.testGraph import create_test_subgraph

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
            temperature=0.7  # Higher temperature for test evaluation
        )

        # Agregar nodos
        graph_builder.add_node("agent", self.think)
        graph_builder.add_node("rag_search", self.rag_search)
        graph_builder.add_node("get_guia", self.get_guia)
        graph_builder.add_node("web_search", self.web_search)
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
                "web_search": "web_search",
                "generate_test": "test_session",  # Route to subgraph node!
                END: END
            },
        )
        graph_builder.add_edge("rag_search", "agent")
        graph_builder.add_edge("get_guia", "agent")
        graph_builder.add_edge("web_search", "agent")
        graph_builder.add_edge("test_session", "agent")  # Subgraph returns to agent

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

        state = {"messages": [HumanMessage(content=query)], "asignatura": asignatura, "context": []}
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
        
        config = {"configurable": {"thread_id": id}}
        
        # Resume using Command with the user's answer
        return self._graph.invoke(Command(resume=resume_value), config=config)