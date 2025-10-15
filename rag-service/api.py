"""FastAPI application for RAG service."""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import logging

from rag_service.config import settings
from rag_service.models import (
    QueryRequest,
    QueryResponse,
    Document,
    IndexResponse,
)
from rag_service.vector_store import get_vector_store

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="RAG Service",
    description="Retrieval-Augmented Generation service for educational chatbot",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "RAG Service",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        vector_store = get_vector_store()
        collection_info = vector_store.get_collection_info()
        
        return {
            "status": "healthy",
            "qdrant_connected": True,
            "collection": collection_info,
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unhealthy: {str(e)}"
        )


@app.post("/search", response_model=QueryResponse)
async def search(request: QueryRequest):
    """
    Semantic search endpoint.
    
    Args:
        request: Query request with optional filters
        
    Returns:
        Query response with search results
    """
    try:
        vector_store = get_vector_store()
        
        # Build filters
        filters = {}
        if request.asignatura:
            filters["asignatura"] = request.asignatura
        if request.tipo_documento:
            filters["tipo_documento"] = request.tipo_documento
        
        # Perform search
        results = vector_store.search(
            query=request.query,
            top_k=request.top_k or settings.top_k_results,
            score_threshold=request.similarity_threshold or settings.similarity_threshold,
            filters=filters if filters else None,
        )
        
        return QueryResponse(
            results=results,
            total_results=len(results),
            query=request.query,
        )
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@app.post("/index", response_model=IndexResponse)
async def index_documents(documents: List[Document]):
    """
    Index documents endpoint.
    
    Args:
        documents: List of documents to index
        
    Returns:
        Index response with count of indexed documents
    """
    try:
        vector_store = get_vector_store()
        
        indexed_count = vector_store.index_documents(documents)
        
        return IndexResponse(
            indexed_count=indexed_count,
            collection_name=settings.qdrant_collection_name,
        )
        
    except Exception as e:
        logger.error(f"Indexing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Indexing failed: {str(e)}"
        )


@app.get("/collection/info")
async def get_collection_info():
    """Get collection information."""
    try:
        vector_store = get_vector_store()
        return vector_store.get_collection_info()
    except Exception as e:
        logger.error(f"Error getting collection info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get collection info: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )
