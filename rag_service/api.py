"""
FastAPI application for the RAG (Retrieval-Augmented Generation) service.

This service provides a REST API for document management and semantic search
functionality to support the TFG chatbot. It handles file uploads, document
indexing, and retrieval operations using Qdrant vector database.

Architecture:
    - File Management: Upload, list, and load documents
    - Document Processing: Text extraction, chunking, embedding generation
    - Vector Storage: Qdrant for efficient semantic search
    - Search API: Semantic search with metadata filtering

Main Routes:
    - /health: Health check endpoint
    - /files: File management endpoints
    - /search: Semantic search endpoint
    - /index: Document indexing endpoint
    - /subjects: Subject and document type discovery

The service runs independently and can be accessed by the main backend
through HTTP requests for RAG operations.

Example:
    Start the service:
        uvicorn rag_service.api:app --reload --port 8001

    Or use the Docker container:
        docker compose up rag_service
"""

__version__ = "0.1.0"

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from rag_service.config import settings
from rag_service.routes.files import router as files_router
from rag_service.routes.general import router as general_router
from rag_service.routes.search_index import router as search_index_router
from rag_service.routes.subjects import router as subjects_router

# Create FastAPI app
app = FastAPI(
    title="RAG Service",
    description="Retrieval-Augmented Generation service for educational chatbot",
    version=__version__,
)

# Ensure a default logging configuration so module loggers (e.g. rag_service.*)
# emit INFO-level logs when the app is run directly (uvicorn may also configure
# logging, but having a basicConfig here ensures logs appear in development).
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(general_router)
app.include_router(search_index_router)
app.include_router(files_router)
app.include_router(subjects_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "rag_service.api:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )
