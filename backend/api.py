""" Backend module for TFG-Chatbot

This module implements the logicfor the AI agent, including:
- Agent Graph
- Tools
- Prompts

"""

__version__ = "0.1.0"

import os
from dotenv import load_dotenv
from fastapi import FastAPI, status
from backend.models import ChatRequest, MessageResponse, ChatResponse, ResumeRequest, InterruptInfo
from backend.logic.graph import GraphAgent
from backend.models import ScrapeRequest, ScrapeResponse
from backend.logic.tools.guia_docente_scraper import UGRTeachingGuideScraper
from backend.db.mongo import MongoDBClient
from backend.models import SubjectItem, SubjectsListResponse
from fastapi import HTTPException

load_dotenv()

app = FastAPI(
    title="TFG Chatbot API",
    description="API for interacting with an intelligent chatbot powered by GraphAgent",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Create a single GraphAgent instance for the whole process. Reusing the
# same compiled graph/checkpointer across requests avoids resume problems
# that happen when different GraphAgent instances (and compiled graphs)
# are created per-request.
# Use LLM_PROVIDER env var to select between vllm and gemini
llm_provider = os.getenv("LLM_PROVIDER", "vllm")
agente = GraphAgent(llm_provider=llm_provider)

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
        "version": __version__,
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
    description="Send a message to the chatbot and receive an intelligent response powered by GraphAgent. May return an interrupt if the bot is waiting for user input (e.g., during a test session).",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "Successful chatbot response. Check 'interrupted' field to see if waiting for user input.",
        },
        422: {
            "description": "Validation error - invalid request format"
        }
    }
)
async def chat(chat_request: ChatRequest):
    respuesta = agente.call_agent(
        query=chat_request.query,
        id=chat_request.id,
        asignatura=chat_request.asignatura,
    )
    
    # Check for interrupt
    if "__interrupt__" in respuesta and respuesta["__interrupt__"]:
        interrupt_data = respuesta["__interrupt__"][0].value
        
        return ChatResponse(
            messages=respuesta.get("messages", []),
            interrupted=True,
            interrupt_info=InterruptInfo(**interrupt_data)
        )
    
    # Normal response without interruption
    return ChatResponse(
        messages=respuesta.get("messages", []),
        interrupted=False
    )


@app.post(
    "/resume_chat",
    tags=["Chatbot"],
    summary="Resume an interrupted test session",
    description="Resume a test session that was interrupted waiting for user input. Provide the user's answer to continue.",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "Successful resume. May return another interrupt if there are more questions.",
        },
        422: {
            "description": "Validation error - invalid request format"
        }
    }
)
async def resume_chat(resume_request: ResumeRequest):
    respuesta = agente.call_agent_resume(
        id=resume_request.id,
        resume_value=resume_request.user_response,
    )
    
    # Check if there's another interrupt (next question)
    if "__interrupt__" in respuesta and respuesta["__interrupt__"]:
        interrupt_data = respuesta["__interrupt__"][0].value
        
        return ChatResponse(
            messages=respuesta.get("messages", []),
            interrupted=True,
            interrupt_info=InterruptInfo(**interrupt_data)
        )
    
    # Test completed or normal flow
    return ChatResponse(
        messages=respuesta.get("messages", []),
        interrupted=False
    )



@app.post(
    "/scrape_guia",
    tags=["Tools"],
    summary="Scrape a guia_docente HTML and index it into MongoDB",
    response_model=ScrapeResponse,
)
async def scrape_guia(req: ScrapeRequest):
    """Parse provided HTML with the scraper and upsert the result into MongoDB.

    The stored document will include a `subject` top-level key (taken from `asignatura` or `subject_override`).
    """
    scraper = UGRTeachingGuideScraper(req.html_content, url=req.url or "")
    data = scraper.parse()

    if req.subject_override:
        data["asignatura"] = req.subject_override

    client = MongoDBClient()
    try:
        client.connect()
        # Prepare document and ensure subject key
        subject = data.get("asignatura")
        if not subject:
            raise ValueError("No subject found in parsed guia; provide subject_override or ensure 'asignatura' is present in the HTML")

        doc = data.copy()
        doc["subject"] = subject

        res = client.upsert("guias", {"subject": subject}, doc)
        return ScrapeResponse(status="ok", subject=subject, upserted_id=res.get("upserted_id"), detail=res)
    except Exception as e:
        return ScrapeResponse(status="error", subject=data.get("asignatura"), detail={"error": str(e)})
    finally:
        client.close()