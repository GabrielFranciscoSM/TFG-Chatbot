"""Clase que encapsula la construcción del grafo y la llamada al agente."""

import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, ToolMessage, HumanMessage
from langgraph.graph import StateGraph, END, MessagesState
from typing import TypedDict, Optional, List, Dict, Any


class SubjectState(MessagesState):
    """Graph state that includes conversation messages, selected asignatura
    and a retrieval `context` where tool nodes can store document snippets.
    """
    asignatura: Optional[str]
    # `context` will hold a list of document snippets returned by RAG tools
    context: Optional[List[Dict[str, Any]]]
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.sqlite import SqliteSaver

from backend.logic.tools.tools import get_tools
from backend.logic.prompts import SYSTEM_PROMPT_V1, SYSTEM_PROMPT_V2

import sqlite3

# --- CONFIGURACIÓN ---
load_dotenv()


class GraphAgent:
    """Clase que encapsula la construcción del grafo y la llamada al agente."""

    def __init__(self, *, vllm_port: str | None = None, model_dir: str | None = None,
                 openai_api_key: str = "EMPTY", temperature: float = 0.1):

        vllm_port = vllm_port or os.getenv("VLLM_MAIN_PORT", "8000")
        vllm_host = os.getenv("VLLM_HOST", "vllm-openai")

        self.vllm_url = f"http://{vllm_host}:{vllm_port}/v1"
        self.model_name = model_dir or os.getenv(
            "MODEL_PATH", "/models/HuggingFaceTB--SmolLM2-1.7B-Instruct"
        )
        self.openai_api_key = openai_api_key
        self.temperature = temperature

        # Cache interno del grafo compilado
        self._graph = None

    def think(self, state: SubjectState):
        """Nodo del Agente. Contesta a la pregunta dada o decide usar herramientas."""
        tools = get_tools()
        system_message = SystemMessage(content=SYSTEM_PROMPT_V2)

        messages = state["messages"]
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [system_message] + messages

        llm = ChatOpenAI(
            model=self.model_name,
            openai_api_key=self.openai_api_key,
            openai_api_base=self.vllm_url,
            temperature=self.temperature,
        ).bind_tools(tools)

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

        # Use the SubjectState so tools can inject 'asignatura' into tool args
        graph_builder = StateGraph(SubjectState)

        # Agregar nodos
        graph_builder.add_node("agent", self.think)
        graph_builder.add_node("rag_search", self.rag_search)
        graph_builder.add_node("get_guia", self.get_guia)
        graph_builder.add_node("web_search", self.web_search)

        # Definir el punto de entrada
        graph_builder.set_entry_point("agent")

        # Agregar aristas 
        graph_builder.add_conditional_edges(
            "agent",
            self.should_continue,
            {"rag_search": "rag_search", "get_guia": "get_guia", "web_search": "web_search", END: END},
        )
        graph_builder.add_edge("rag_search", "agent")
        graph_builder.add_edge("get_guia", "agent")
        graph_builder.add_edge("web_search", "agent")

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