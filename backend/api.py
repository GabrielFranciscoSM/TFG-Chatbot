"""
Backend API for the TFG Chatbot.

This module implements the main FastAPI application that exposes the AI agent
functionality through REST endpoints. The backend handles:

- Chat interactions with the intelligent agent powered by LangGraph
- Test session management with interrupts and resume capabilities
- Web scraping of UGR teaching guides (guías docentes)
- Integration with MongoDB for storing teaching guide data
- Integration with RAG service for semantic search

Architecture:
    The backend uses a single GraphAgent instance shared across all requests
    to maintain conversation state and checkpointing. This ensures proper
    session management and allows users to resume interrupted conversations.

Key Components:
    - GraphAgent: Orchestrates the conversation flow using LangGraph
    - MongoDB: Stores teaching guide data for quick retrieval
    - RAG Service: Provides semantic search capabilities (separate service)
    - LLM Provider: Configurable (vLLM or Gemini) via LLM_PROVIDER env var

Main Endpoints:
    - POST /chat: Send messages and receive intelligent responses
    - POST /resume_chat: Resume interrupted test sessions
    - POST /scrape_guia: Parse and store teaching guides
    - GET /health: Health check endpoint

Example:
    Start the backend:
        uvicorn backend.api:app --reload --port 8000

    Or use Docker:
        docker compose up backend

    Chat with the bot:
        POST http://localhost:8000/chat
        {
            "query": "¿Qué es Docker?",
            "id": "session_123",
            "asignatura": "iv"
        }
"""

__version__ = "0.1.0"

import os
from typing import Literal, cast

from dotenv import load_dotenv
from fastapi import FastAPI, status

from backend.db.mongo import MongoDBClient
from backend.logic.graph import GraphAgent
from backend.logic.tools.guia_docente_scraper import UGRTeachingGuideScraper
from backend.models import (
    ChatRequest,
    ChatResponse,
    InterruptInfo,
    MessageResponse,
    ResumeRequest,
    ScrapeRequest,
    ScrapeResponse,
)

load_dotenv()

app = FastAPI(
    title="TFG Chatbot API",
    description="API for interacting with an intelligent chatbot powered by GraphAgent",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Create a single GraphAgent instance for the whole process. Reusing the
# same compiled graph/checkpointer across requests avoids resume problems
# that happen when different GraphAgent instances (and compiled graphs)
# are created per-request.
# Use LLM_PROVIDER env var to select between vllm and gemini
llm_provider_str = os.getenv("LLM_PROVIDER", "vllm")
llm_provider = cast(
    Literal["vllm", "gemini"],
    llm_provider_str if llm_provider_str in ["vllm", "gemini"] else "vllm",
)
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
                            "redoc": "/redoc",
                        },
                    }
                }
            },
        }
    },
)
async def root():
    """
    Get API information and available endpoints.

    Returns basic information about the TFG Chatbot API including version,
    description, and links to all available endpoints.

    Returns:
        Dict with API metadata and endpoint descriptions
    """
    return {
        "name": "TFG Chatbot API",
        "version": __version__,
        "description": "API for interacting with an intelligent chatbot powered by GraphAgent",
        "status": "running",
        "endpoints": {
            "health": "/health - Health check endpoint",
            "chat": "/chat - Send messages to the chatbot",
            "docs": "/docs - Interactive API documentation (Swagger UI)",
            "redoc": "/redoc - Alternative API documentation (ReDoc)",
        },
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
            "content": {"application/json": {"example": {"message": "Hello World"}}},
        }
    },
)
async def health():
    """
    Health check endpoint.

    Simple endpoint to verify the API is running and accessible.
    Used for monitoring and load balancer health checks.

    Returns:
        MessageResponse with "Hello World" message
    """
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
        422: {"description": "Validation error - invalid request format"},
    },
)
async def chat(chat_request: ChatRequest):
    """
    Send a message to the chatbot and receive an intelligent response.

    The chatbot uses GraphAgent to orchestrate the conversation flow, which includes:
    - Understanding user intent
    - Searching for relevant information using RAG
    - Consulting teaching guides stored in MongoDB
    - Generating appropriate responses
    - Managing test sessions with interrupts

    If the bot initiates a test session, it will return an interrupt with the first
    question. Use the /resume_chat endpoint to continue the test.

    Args:
        chat_request: ChatRequest containing query, session ID, and optional subject

    Returns:
        ChatResponse with messages and interrupt information if applicable

    Example:
        Request:
        {
            "query": "¿Qué es integración continua?",
            "id": "user_session_123",
            "asignatura": "iv"
        }

        Response (normal):
        {
            "messages": [...],
            "interrupted": false
        }

        Response (test interrupt):
        {
            "messages": [...],
            "interrupted": true,
            "interrupt_info": {
                "question_text": "¿Qué herramienta...",
                "options": ["A", "B", "C", "D"],
                "question_number": 1,
                "total_questions": 5
            }
        }
    """
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
            interrupt_info=InterruptInfo(**interrupt_data),
        )

    # Normal response without interruption
    return ChatResponse(messages=respuesta.get("messages", []), interrupted=False)


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
        422: {"description": "Validation error - invalid request format"},
    },
)
async def resume_chat(resume_request: ResumeRequest):
    """
    Resume an interrupted test session with the user's answer.

    When the bot interrupts with a test question, use this endpoint to provide
    the user's answer and continue the test. The bot will either:
    - Return the next question (another interrupt)
    - Complete the test and provide results (no interrupt)

    The session is maintained using the thread ID from the original chat request.

    Args:
        resume_request: ResumeRequest with session ID and user's answer

    Returns:
        ChatResponse with evaluation and next question or final results

    Example:
        Request:
        {
            "id": "user_session_123",
            "user_response": "B"
        }

        Response (next question):
        {
            "messages": [
                {"role": "assistant", "content": "Correcto! La respuesta es B..."}
            ],
            "interrupted": true,
            "interrupt_info": {
                "question_text": "Segunda pregunta...",
                ...
            }
        }

        Response (test completed):
        {
            "messages": [
                {"role": "assistant", "content": "¡Test completado! Tu puntuación: 4/5"}
            ],
            "interrupted": false
        }
    """
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
            interrupt_info=InterruptInfo(**interrupt_data),
        )

    # Test completed or normal flow
    return ChatResponse(messages=respuesta.get("messages", []), interrupted=False)


@app.post(
    "/scrape_guia",
    tags=["Tools"],
    summary="Scrape a guia_docente HTML and index it into MongoDB",
    response_model=ScrapeResponse,
)
async def scrape_guia(req: ScrapeRequest):
    """
    Parse a UGR teaching guide HTML and store it in MongoDB.

    This endpoint processes the HTML content of a teaching guide (guía docente)
    from the University of Granada, extracts structured information, and stores
    it in MongoDB for quick retrieval by the chatbot.

    The scraper extracts:
    - Course information (name, code, credits)
    - Competencies and learning objectives
    - Course content and topics
    - Teaching methodology
    - Evaluation criteria
    - Bibliography

    Args:
        req: ScrapeRequest with HTML content, optional URL, and subject override

    Returns:
        ScrapeResponse with status, subject, and MongoDB upsert result

    Raises:
        ValueError: If no subject can be determined from the HTML or override

    Example:
        Request:
        {
            "html_content": "<html>...</html>",
            "url": "https://...",
            "subject_override": "infraestructura-virtual"
        }

        Response:
        {
            "status": "ok",
            "subject": "infraestructura-virtual",
            "upserted_id": "507f1f77bcf86cd799439011",
            "detail": {...}
        }
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
            raise ValueError(
                "No subject found in parsed guia; provide subject_override or ensure 'asignatura' is present in the HTML"
            )

        doc = data.copy()
        doc["subject"] = subject

        res = client.upsert("guias", {"subject": subject}, doc)
        return ScrapeResponse(
            status="ok", subject=subject, upserted_id=res.get("upserted_id"), detail=res
        )
    except Exception as e:
        return ScrapeResponse(
            status="error", subject=data.get("asignatura"), detail={"error": str(e)}
        )
    finally:
        client.close()
