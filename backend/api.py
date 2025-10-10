from fastapi import FastAPI, status
from models import ChatRequest, MessageResponse
from logic.graph import GraphAgent

# Define version directly or import it properly
backend_version = "0.1.0"

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
    summary="API Information",
    description="Returns information about the TFG Chatbot API including version, available endpoints, and documentation links",
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "Successful response with API information",
            "content": {
                "application/json": {
                    "example": {
                        "name": "TFG Chatbot API",
                        "version": "0.1.0",
                        "description": "API for interacting with an intelligent chatbot powered by GraphAgent",
                        "endpoints": {
                            "health": "/health",
                            "chat": "/chat",
                            "docs": "/docs",
                            "redoc": "/redoc"
                        }
                    }
                }
            }
        }
    }
)
async def root():
    return {
        "name": "TFG Chatbot API",
        "version": backend_version,
        "description": "API for interacting with an intelligent chatbot powered by GraphAgent",
        "status": "running",
        "endpoints": {
            "health": "/health - Health check endpoint",
            "chat": "/chat - Send messages to the chatbot",
            "docs": "/docs - Interactive API documentation (Swagger UI)",
            "redoc": "/redoc - Alternative API documentation (ReDoc)"
        }
    }


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