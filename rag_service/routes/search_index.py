"""Search and indexing endpoints."""

from fastapi import APIRouter, HTTPException, status
from typing import List
import logging
from ..models import QueryRequest, QueryResponse, Document, IndexResponse
from ..embeddings.store import get_vector_store
from ..config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post(
    "/search",
    tags=["Search"],
    summary="Semantic search",
    response_model=QueryResponse,
    status_code=status.HTTP_200_OK,
)
async def search(request: QueryRequest):
    try:
        vector_store = get_vector_store()
        filters = {}
        if request.asignatura:
            filters["asignatura"] = request.asignatura
        if request.tipo_documento:
            filters["tipo_documento"] = request.tipo_documento
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

@router.post(
    "/index",
    tags=["Indexing"],
    summary="Index documents",
    response_model=IndexResponse,
    status_code=status.HTTP_200_OK,
)
async def index_documents(documents: List[Document]):
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

@router.get(
    "/collection/info",
    tags=["Collection"],
    summary="Get collection information",
    status_code=status.HTTP_200_OK,
)
async def get_collection_info():
    try:
        vector_store = get_vector_store()
        return vector_store.get_collection_info()
    except Exception as e:
        logger.error(f"Error getting collection info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get collection info: {str(e)}"
        )
