import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, MessagesState
from langgraph.prebuilt import ToolNode
from .tools import get_tools
from .prompts import SYSTEM_PROMPT, SYSTEM_PROMPT_SMOLLM2
from langchain_core.messages import SystemMessage
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

# --- CONFIGURACIÓN ---
load_dotenv()


class GraphAgent:
    """Clase que encapsula la construcción del grafo y la llamada al agente.

    Mantiene la API existente a nivel de módulo (think, should_continue, build_graph)
    y añade un método `call_agent(query, id)` para invocar el agente desde fuera.
    """

    def __init__(self, *, vllm_port: str | None = None, model_dir: str | None = None,
                 openai_api_key: str = "EMPTY", temperature: float = 0.1):
        # Lectura de configuración desde entorno si no se pasan parámetros
        vllm_port = vllm_port or os.getenv("VLLM_MAIN_PORT", "8000")
        self.vllm_url = "http://localhost:" + vllm_port + "/v1"
        self.model_name = model_dir or os.getenv(
            "MODEL_PATH", "/models/HuggingFaceTB--SmolLM2-1.7B-Instruct"
        )
        self.openai_api_key = openai_api_key
        self.temperature = temperature

        # Cache interno del grafo compilado
        self._graph = None

    def think(self, state: MessagesState):
        """Nodo del Agente. Contesta a la pregunta dada o decide usar herramientas."""
        tools = get_tools()
        system_message = SystemMessage(content=SYSTEM_PROMPT_SMOLLM2)

        messages = state["messages"]
        # Check if there's already a system message
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [system_message] + messages

        print("messages:", messages)

        print(self.model_name, self.vllm_url)
        llm = ChatOpenAI(
            model=self.model_name,
            openai_api_key=self.openai_api_key,
            openai_api_base=self.vllm_url,
            temperature=self.temperature,
        ).bind_tools(tools)

        # Pass the messages as a list, not as concatenated string
        # This preserves the conversation structure and tool messages
        response = llm.invoke(messages)
        
        print("=" * 80)
        print("AI RESPONSE:")
        print(f"Content: {response.content}")
        print(f"Tool calls: {getattr(response, 'tool_calls', None)}")
        print(f"Additional kwargs: {getattr(response, 'additional_kwargs', None)}")
        print("=" * 80)

        return {"messages": [response]}

    def should_continue(self, state: MessagesState):
        """Decide si el agente debe continuar o terminar."""
        messages = state["messages"]
        last_message = messages[-1]

        # Si el último mensaje tiene tool_calls, continuar a las herramientas
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        # Si no, terminar
        return END

    def build_graph(self):
        """Construye y compila el grafo del agente y lo cachea en self._graph."""
        tools = get_tools()

        graph_builder = StateGraph(MessagesState)

        # Agregar nodos
        graph_builder.add_node("agent", self.think)
        graph_builder.add_node("tools", ToolNode(tools))

        # Definir el punto de entrada
        graph_builder.set_entry_point("agent")

        # Agregar aristas condicionales
        graph_builder.add_conditional_edges(
            "agent",
            self.should_continue,
            {"tools": "tools", END: END},
        )

        # Add edge from tools back to agent
        graph_builder.add_edge("tools", "agent")

        # Preparar persistencia
        storage_dir = os.path.join(os.path.dirname(__file__), "storage")
        os.makedirs(storage_dir, exist_ok=True)
        checkpoint_path = os.path.join(storage_dir, "checkpoints.db")
        conn = sqlite3.connect(checkpoint_path, check_same_thread=False)
        memory = SqliteSaver(conn)

        self._graph = graph_builder.compile(checkpointer=memory)
        return self._graph

    def call_agent(self, query: str, id: str):
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

        # Importar aquí para evitar importaciones no usadas si no se llama
        from langchain_core.messages import HumanMessage

        state = {"messages": [HumanMessage(content=query)]}
        config = {"configurable": {"thread_id": id}}

        return self._graph.invoke(state, config=config)