from fastapi import FastAPI, status
from .models import ChatRequest, MessageResponse
from .logic import GraphAgent
from . import __version__ as backend_version

app = FastAPI(
    title="TFG Chatbot API",
    description="API for interacting with an intelligent chatbot powered by GraphAgent",
    version=backend_version,
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.get(
    "/", 
    tags=["General"],
    summary="Root endpoint",
    description="Welcome endpoint that returns a simple greeting message",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "Successful response",
            "content": {
                "application/json": {
                    "example": {"message": "Hello World"}
                }
            }
        }
    }
)
async def root():
    return {"message": "Hello World"}


@app.get(
    "/health", 
    tags=["General"],
    summary="Health check",
    description="Check if the API is running and healthy",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "API is healthy and running",
            "content": {
                "application/json": {
                    "example": {"message": "Hello World"}
                }
            }
        }
    }
)
async def health():
    return {"message": "Hello World"}


@app.post(
    "/chat", 
    tags=["Chatbot"],
    summary="Chat with the bot",
    description="Send a message to the chatbot and receive an intelligent response powered by GraphAgent",
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "Successful chatbot response",
        },
        422: {
            "description": "Validation error - invalid request format"
        }
    }
)
async def chat(chat_request: ChatRequest):
    agente = GraphAgent()
    respuesta = agente.call_agent(query=chat_request.query,id=chat_request.id)
    return respuesta