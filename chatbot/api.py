"""
Backend API for the TFG Chatbot.

This module implements the main FastAPI application that exposes the AI agent
functionality through REST endpoints. The chatbot handles:

- Chat interactions with the intelligent agent powered by LangGraph
- Test session management with interrupts and resume capabilities
- Web scraping of UGR teaching guides (guías docentes)
- Integration with MongoDB for storing teaching guide data
- Integration with RAG service for semantic search

Architecture:
    The chatbot uses a single GraphAgent instance shared across all requests
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
    Start the chatbot:
        uvicorn chatbot.api:app --reload --port 8000

    Or use Docker:
        docker compose up chatbot

    Chat with the bot:
        POST http://localhost:8000/chat
        {
            "query": "¿Qué es Docker?",
            "id": "session_123",
            "asignatura": "iv"
        }
"""

__version__ = "0.1.0"

from fastapi import FastAPI, status
from prometheus_fastapi_instrumentator import Instrumentator

from chatbot.config import settings
from chatbot.db.mongo import MongoDBClient
from chatbot.events import get_event_logger
from chatbot.instrumentation import setup_phoenix_instrumentation
from chatbot.logging_config import CorrelationIdMiddleware, setup_logging
from chatbot.logic.graph import GraphAgent
from chatbot.logic.profile_manager import get_profile_manager
from chatbot.logic.tools.guia_docente_scraper import UGRTeachingGuideScraper
from chatbot.models import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    HistoryResponse,
    InterruptInfo,
    MessageResponse,
    ResumeRequest,
    ScrapeRequest,
    ScrapeResponse,
)


def _extract_text_content(content) -> str:
    """Extract text content from LangChain message content.

    Handles different content formats from various LLM providers:
    - String: returned as-is
    - List of content blocks (Gemini format): extracts text from each block

    Args:
        content: Message content, either a string or a list of content blocks

    Returns:
        Extracted text content as a string
    """
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        # Handle Gemini-style content blocks: [{'type': 'text', 'text': '...'}]
        text_parts = []
        for block in content:
            if isinstance(block, dict):
                # Extract 'text' field from content block
                if "text" in block:
                    text_parts.append(block["text"])
            elif isinstance(block, str):
                text_parts.append(block)
        return "".join(text_parts)

    # Fallback: convert to string
    return str(content)


# Initialize structured logging
setup_logging()

# Initialize Phoenix/OpenInference instrumentation for LLM tracing
# Must be called BEFORE creating ChatModel/LLM instances
setup_phoenix_instrumentation()

app = FastAPI(
    title="TFG Chatbot API",
    description="API for interacting with an intelligent chatbot powered by GraphAgent",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Initialize Prometheus instrumentator for metrics endpoint
Instrumentator().instrument(app).expose(app)

# Add correlation ID middleware
app.add_middleware(CorrelationIdMiddleware)

# Create a single GraphAgent instance for the whole process. Reusing the
# same compiled graph/checkpointer across requests avoids resume problems
# that happen when different GraphAgent instances (and compiled graphs)
# are created per-request.
agente = GraphAgent(llm_provider=settings.llm_provider)


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


@app.get(
    "/system/info",
    tags=["General"],
    summary="System information",
    description="Get information about the chatbot system configuration",
    status_code=status.HTTP_200_OK,
)
async def system_info():
    """
    Get system configuration information.

    Returns the current LLM provider, model name, and system version.
    Used by the frontend to display system information.

    Returns:
        Dict with system configuration details
    """
    # Map provider to display name
    provider_display = {
        "gemini": "Gemini",
        "mistral": "Mistral AI",
        "vllm": "vLLM (Local)",
    }

    # Map provider to model name
    model_display = {
        "gemini": settings.gemini_model,
        "mistral": settings.mistral_model,
        "vllm": (
            settings.model_path.split("/")[-1] if settings.model_path else "Unknown"
        ),
    }

    return {
        "version": __version__,
        "llm_provider": provider_display.get(
            settings.llm_provider, settings.llm_provider
        ),
        "llm_model": model_display.get(settings.llm_provider, "Unknown"),
        "status": "operational",
    }


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
    import time

    start_time = time.time()

    # Log question asked event
    event_logger = get_event_logger()
    event_logger.log_question_asked(
        session_id=chat_request.id,
        query=chat_request.query,
        user_id=chat_request.user_id,
        subject_id=chat_request.asignatura,
    )

    respuesta = agente.call_agent(
        query=chat_request.query,
        id=chat_request.id,
        asignatura=chat_request.asignatura,
    )

    # Extract only the last AI message
    messages = respuesta.get("messages", [])
    last_ai_message = None
    for msg in reversed(messages):
        if hasattr(msg, "type") and msg.type == "ai":
            last_ai_message = ChatMessage(
                type="ai", content=_extract_text_content(msg.content)
            )
            break

    # Extract difficulty from response state
    query_difficulty = respuesta.get("query_difficulty", "unknown")

    # Log answer received event
    latency_ms = (time.time() - start_time) * 1000
    if last_ai_message:
        event_logger.log_answer_received(
            session_id=chat_request.id,
            answer=last_ai_message.content,
            user_id=chat_request.user_id,
            subject_id=chat_request.asignatura,
            latency_ms=latency_ms,
        )

    # Update student profile and save conversation turn
    if chat_request.user_id:
        profile_manager = get_profile_manager()

        # Record the interaction for profile tracking
        profile_manager.record_interaction(
            user_id=chat_request.user_id,
            query=chat_request.query,
            difficulty=query_difficulty or "unknown",
            subject=chat_request.asignatura,
            topic=None,  # TODO: Extract topic from RAG context or LLM
        )

        # Save full conversation turn for analysis
        if last_ai_message:
            profile_manager.save_conversation_turn(
                session_id=chat_request.id,
                query=chat_request.query,
                answer=last_ai_message.content,
                user_id=chat_request.user_id,
                subject=chat_request.asignatura,
                difficulty=query_difficulty,
                latency_ms=latency_ms,
            )

    # Check for interrupt
    if "__interrupt__" in respuesta and respuesta["__interrupt__"]:
        interrupt_data = respuesta["__interrupt__"][0].value

        # When interrupted, if message is empty, use question_text from interrupt
        # This happens because the last AI message is just the tool call
        if last_ai_message is None or not last_ai_message.content:
            question_text = interrupt_data.get("question_text", "")
            question_num = interrupt_data.get("question_num", 1)
            total_questions = interrupt_data.get("total_questions", 1)
            formatted_message = (
                f"📝 Pregunta {question_num}/{total_questions}\n\n{question_text}"
            )
            last_ai_message = ChatMessage(type="ai", content=formatted_message)

        return ChatResponse(
            message=last_ai_message,
            interrupted=True,
            interrupt_info=InterruptInfo(**interrupt_data),
        )

    # Normal response without interruption
    return ChatResponse(message=last_ai_message, interrupted=False)


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

    # Extract only the last AI message
    messages = respuesta.get("messages", [])
    last_ai_message = None
    for msg in reversed(messages):
        if hasattr(msg, "type") and msg.type == "ai":
            last_ai_message = ChatMessage(
                type="ai", content=_extract_text_content(msg.content)
            )
            break

    # Check if there's another interrupt (next question)
    if "__interrupt__" in respuesta and respuesta["__interrupt__"]:
        interrupt_data = respuesta["__interrupt__"][0].value

        # When interrupted, if message is empty, use question_text from interrupt
        if last_ai_message is None or not last_ai_message.content:
            question_text = interrupt_data.get("question_text", "")
            question_num = interrupt_data.get("question_num", 1)
            total_questions = interrupt_data.get("total_questions", 1)
            formatted_message = (
                f"📝 Pregunta {question_num}/{total_questions}\n\n{question_text}"
            )
            last_ai_message = ChatMessage(type="ai", content=formatted_message)

        return ChatResponse(
            message=last_ai_message,
            interrupted=True,
            interrupt_info=InterruptInfo(**interrupt_data),
        )

    # Test completed or normal flow
    return ChatResponse(message=last_ai_message, interrupted=False)


@app.get(
    "/history/{session_id}",
    tags=["Chatbot"],
    summary="Get conversation history",
    description="Retrieve the message history for a specific conversation session.",
    response_model=HistoryResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Conversation history retrieved successfully"},
        404: {"description": "No history found for this session"},
    },
)
async def get_history(session_id: str):
    """
    Get the conversation history for a session.

    Retrieves all messages from the LangGraph checkpointer for the given
    session/thread ID. Returns an empty list if no history exists.

    Args:
        session_id: The thread ID of the conversation

    Returns:
        HistoryResponse with all messages from the conversation
    """
    raw_messages = agente.get_history(id=session_id)
    # Convert LangChain messages to ChatMessage format
    messages = []
    for msg in raw_messages:
        if hasattr(msg, "type") and msg.type in ("human", "ai"):
            messages.append(
                ChatMessage(type=msg.type, content=_extract_text_content(msg.content))
            )
    return HistoryResponse(messages=messages)


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


# --- Analytics Endpoints ---


@app.get(
    "/profiles/{user_id}",
    tags=["Analytics"],
    summary="Get student knowledge profile",
    description="Retrieve the knowledge profile for a student, including mastery levels and interaction history.",
)
async def get_profile(user_id: str):
    """
    Get student knowledge profile for analysis.

    Returns the student's learning profile including difficulty distribution,
    subject mastery levels, recent interactions, and test performance.

    Args:
        user_id: The user identifier

    Returns:
        Student profile data or 404 if not found
    """
    profile_manager = get_profile_manager()
    profile = profile_manager.get_profile(user_id)

    if profile is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Profile not found")

    return profile.model_dump()


@app.get(
    "/conversations",
    tags=["Analytics"],
    summary="Get conversation history",
    description="Retrieve full conversation turns for analysis and research.",
)
async def get_conversations(
    user_id: str | None = None,
    session_id: str | None = None,
    limit: int = 100,
):
    """
    Get conversation history for analysis.

    Returns full conversation turns (question + answer pairs) with metadata.
    Can filter by user_id and/or session_id.

    Args:
        user_id: Optional user filter
        session_id: Optional session filter
        limit: Maximum number of turns to return (default 100)

    Returns:
        List of conversation turns
    """
    profile_manager = get_profile_manager()
    turns = profile_manager.get_conversation_history(
        session_id=session_id,
        user_id=user_id,
        limit=limit,
    )

    return [turn.model_dump() for turn in turns]


@app.post(
    "/profiles/batch",
    tags=["Analytics"],
    summary="Get multiple student profiles",
    description="Retrieve profiles for multiple students at once. Useful for dashboard views.",
)
async def get_profiles_batch(user_ids: list[str]):
    """
    Get multiple student profiles in a single request.

    Returns profiles for the specified user IDs. Users without profiles
    are omitted from the response.

    Args:
        user_ids: List of user identifiers

    Returns:
        List of student profiles that exist
    """
    profile_manager = get_profile_manager()
    profiles = []

    for user_id in user_ids:
        profile = profile_manager.get_profile(user_id)
        if profile is not None:
            profiles.append(profile.model_dump())

    return profiles


@app.get(
    "/conversations/stats",
    tags=["Analytics"],
    summary="Get conversation statistics for users",
    description="Get aggregated statistics for conversations, optionally filtered by users and subject.",
)
async def get_conversation_stats(
    user_ids: str | None = None,
    subject: str | None = None,
):
    """
    Get aggregated conversation statistics.

    Returns statistics like total conversations, difficulty distribution,
    topics discussed, and activity over time.

    Args:
        user_ids: Comma-separated list of user IDs to filter (optional)
        subject: Subject to filter by (optional)

    Returns:
        Aggregated statistics dictionary
    """
    profile_manager = get_profile_manager()
    collection = profile_manager.db_client.get_collection(
        profile_manager.CONVERSATIONS_COLLECTION
    )

    # Build match stage
    match_stage: dict = {}
    if user_ids:
        user_id_list = [uid.strip() for uid in user_ids.split(",")]
        match_stage["user_id"] = {"$in": user_id_list}
    if subject:
        match_stage["subject"] = subject

    # Aggregation pipeline
    pipeline = [
        {"$match": match_stage} if match_stage else {"$match": {}},
        {
            "$group": {
                "_id": None,
                "total_conversations": {"$sum": 1},
                "unique_users": {"$addToSet": "$user_id"},
                "unique_sessions": {"$addToSet": "$session_id"},
                "difficulty_counts": {"$push": "$difficulty"},
                "avg_latency_ms": {"$avg": "$latency_ms"},
                "test_conversations": {"$sum": {"$cond": ["$was_test", 1, 0]}},
            }
        },
    ]

    results = list(collection.aggregate(pipeline))

    if not results:
        return {
            "total_conversations": 0,
            "unique_users": 0,
            "unique_sessions": 0,
            "difficulty_distribution": {},
            "avg_latency_ms": None,
            "test_conversations": 0,
        }

    result = results[0]

    # Count difficulty distribution
    difficulty_dist: dict[str, int] = {}
    for diff in result.get("difficulty_counts", []):
        if diff:
            difficulty_dist[diff] = difficulty_dist.get(diff, 0) + 1

    return {
        "total_conversations": result["total_conversations"],
        "unique_users": len(result.get("unique_users", [])),
        "unique_sessions": len(result.get("unique_sessions", [])),
        "difficulty_distribution": difficulty_dist,
        "avg_latency_ms": result.get("avg_latency_ms"),
        "test_conversations": result.get("test_conversations", 0),
    }
