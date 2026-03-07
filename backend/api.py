import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from backend.config import settings
from backend.logging_config import CorrelationIdMiddleware, setup_logging
from backend.routers import (
    admin,
    auth,
    chat,
    faqs,
    professor,
    sessions,
    subjects,
    topics,
    users,
)

# Initialize structured logging
setup_logging()

app = FastAPI(title="TFG Chatbot Backend")

# Initialize Prometheus instrumentator
Instrumentator().instrument(app).expose(app)

# Add correlation ID middleware
app.add_middleware(CorrelationIdMiddleware)

# CORS configuration for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Production frontend container
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(subjects.router)
app.include_router(subjects.public_router)
app.include_router(professor.router)
app.include_router(sessions.router)
app.include_router(chat.router)
app.include_router(faqs.router)
app.include_router(faqs.public_router)
app.include_router(topics.router)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/system/info")
async def system_info():
    """
    Get system information from the chatbot service.

    Proxies to the chatbot's /system/info endpoint to get LLM configuration.
    Returns a fallback response if the chatbot service is unavailable.
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.chatbot_service_url}/system/info")
            response.raise_for_status()
            return response.json()
    except Exception:
        # Return fallback if chatbot service is unavailable
        return {
            "version": "unknown",
            "llm_provider": "Unknown",
            "llm_model": "Unknown",
            "status": "unavailable",
        }
