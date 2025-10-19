"""General endpoints: root and health check."""

from fastapi import APIRouter, status
from ..models import HealthCheckResponse
from ..embeddings.store import get_vector_store
import logging
from ..config import settings

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
        "name": "RAG Service",
        "version": settings.api_version if hasattr(settings, 'api_version') else "0.1.0",
        "description": "API for interacting with a Retrieval-Augmented Generation service",
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
    try:
        vector_store = get_vector_store()
        collection_info = vector_store.get_collection_info()
        return HealthCheckResponse(
            status="healthy",
            qdrant_connected=True,
            collection=collection_info,
            message="API is healthy and running"
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthCheckResponse(
            status="unhealthy",
            qdrant_connected=False,
            collection=None,
            message="Service unhealthy: " + str(e)
        )
