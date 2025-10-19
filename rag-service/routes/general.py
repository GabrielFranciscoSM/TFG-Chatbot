"""General endpoints: root and health check."""

from fastapi import APIRouter, status
from rag_service.models import HealthCheckResponse
from rag_service.vector_store import get_vector_store
import logging
from rag_service.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get(
    "/", 
    tags=["General"],
    summary="API Information",
    description="Returns information about the RAG Service API including version, available endpoints, and documentation links",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Successful response with API information"}
    }
)
async def root():
    """Root endpoint."""
    return {
        "name": "RAG Service",
        "version": settings.api_version if hasattr(settings, 'api_version') else "0.1.0",
        "description": "API for interacting with a Retrieval-Augmented Generation service",
        "status": "running",
        "endpoints": {
            "health": "/health - Health check endpoint",
            "search": "/search - Semantic search endpoint",
            "index": "/index - Index documents endpoint",
            "docs": "/docs - Interactive API documentation (Swagger UI)",
            "redoc": "/redoc - Alternative API documentation (ReDoc)",
            "files": "/files - List available files",
            "subjects": "/subjects - List available subjects",
            "upload": "/upload - Upload and optionally index a file",
            "load-file": "/load-file - Load and index a file from documents directory",
            "collection/info": "/collection/info - Get collection information",
            "files/{filename}": "/files/{filename} - Get information about a specific file",
            "subjects/{asignatura}/types": "/subjects/{asignatura}/types - List document types for a subject",
        }
    }

@router.get(
    "/health",
    tags=["General"],
    summary="Health check",
    description="Check if the API is running and healthy",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "API is healthy and running",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "qdrant_connected": True,
                        "collection": {"name": "academic_documents", "vectors_count": 0, "points_count": 52, "status": "green"},
                        "message": "API is healthy and running"
                    }
                }
            }
        }
    }
)
async def health_check():
    """Health check endpoint."""
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
