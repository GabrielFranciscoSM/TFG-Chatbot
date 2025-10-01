import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, MessagesState

# --- CONFIGURACIÓN ---
load_dotenv()

VLLM_URL = "http://localhost:" + os.getenv("VLLM_MAIN_PORT", "8000") + "/v1"
VLLM_MODEL_NAME = os.getenv("MODEL_DIR", "/models/unsloth--mistral-7b-instruct-v0.3-bnb-4bit")

# --- LÓGICA DEL GRAFO ---

def think(state: MessagesState):
    """Nodo del Agente. COntesta a la pregunta dada"""

    llm = ChatOpenAI(
        model=VLLM_MODEL_NAME, 
        openai_api_key="EMPTY", 
        openai_api_base=VLLM_URL, 
        temperature=0
        )
    
    response = llm.invoke(state["messages"])

    return {"messages": [response]}

# --- CONSTRUCCIÓN DEL GRAFO ---

def build_graph():
    """Construye y compila el grafo del agente."""
    graph_builder = StateGraph(MessagesState)
    
    graph_builder.add_node("agent", think)
    graph_builder.set_entry_point("agent")

    return graph_builder.compile()
