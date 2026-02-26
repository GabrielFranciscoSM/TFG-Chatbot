"""General endpoints: root and health check."""

import logging

from fastapi import APIRouter, status
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from math_service.config import settings
from math_service.models import HealthCheckResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/",
    tags=["General"],
    summary="API Information",
    status_code=status.HTTP_200_OK,
)
async def root():
    return {
        "name": "Math Service",
        "version": "0.1.0",
        "description": "Mathematical analysis service (FAQ generation, topic extraction)",
        "status": "running",
    }


@router.get(
    "/health",
    tags=["General"],
    summary="Health check",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
)
async def health_check():
    mongo_ok = False
    ollama_ok = False

    # Check MongoDB connectivity
    try:
        mongo_uri = settings.get_mongo_uri()
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=2000)
        client.admin.command("ping")
        mongo_ok = True
        client.close()
    except (ConnectionFailure, Exception) as e:
        logger.warning(f"MongoDB health check failed: {e}")

    # Check Ollama connectivity
    try:
        import httpx

        resp = httpx.get(
            f"http://{settings.ollama_host}:{settings.ollama_port}/api/tags",
            timeout=2.0,
        )
        ollama_ok = resp.status_code == 200
    except Exception as e:
        logger.warning(f"Ollama health check failed: {e}")

    overall = "healthy" if (mongo_ok and ollama_ok) else "degraded"
    return HealthCheckResponse(
        status=overall,
        mongo_connected=mongo_ok,
        ollama_connected=ollama_ok,
        message=f"MongoDB: {'OK' if mongo_ok else 'FAIL'}, Ollama: {'OK' if ollama_ok else 'FAIL'}",
    )
