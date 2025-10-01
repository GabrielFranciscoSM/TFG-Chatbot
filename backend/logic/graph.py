import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, MessagesState
from langgraph.prebuilt import ToolNode
from .tools import get_tools

# --- CONFIGURACIÓN ---
load_dotenv()

VLLM_URL = "http://localhost:" + os.getenv("VLLM_MAIN_PORT", "8000") + "/v1"
VLLM_MODEL_NAME = os.getenv("MODEL_DIR", "/models/unsloth--mistral-7b-instruct-v0.3-bnb-4bit")

# --- LÓGICA DEL GRAFO ---

def should_continue(state: MessagesState):
    """Decide si el agente debe continuar o terminar."""
    messages = state["messages"]
    last_message = messages[-1]
    
    # Si el último mensaje tiene tool_calls, continuar a las herramientas
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    # Si no, terminar
    return END


def think(state: MessagesState):
    """Nodo del Agente. Contesta a la pregunta dada o decide usar herramientas."""
    tools = get_tools()
    
    llm = ChatOpenAI(
        model=VLLM_MODEL_NAME, 
        openai_api_key="EMPTY", 
        openai_api_base=VLLM_URL, 
        temperature=0
    ).bind_tools(tools)
    
    response = llm.invoke(state["messages"])

    return {"messages": [response]}

# --- CONSTRUCCIÓN DEL GRAFO ---

def build_graph():
    """Construye y compila el grafo del agente."""
    tools = get_tools()
    graph_builder = StateGraph(MessagesState)
    
    # Agregar nodos
    graph_builder.add_node("agent", think)
    graph_builder.add_node("tools", ToolNode(tools))
    
    # Definir el punto de entrada
    graph_builder.set_entry_point("agent")
    
    # Agregar aristas condicionales
    graph_builder.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            END: END
        }
    )
    
    # Después de usar herramientas, volver al agente
    graph_builder.add_edge("tools", "agent")

    return graph_builder.compile()
