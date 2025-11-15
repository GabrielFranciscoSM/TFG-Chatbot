"""Search and indexing endpoints."""

import logging

from fastapi import APIRouter, HTTPException, status

from rag_service.config import settings
from rag_service.embeddings.store import get_vector_store
from rag_service.models import Document, IndexResponse, QueryRequest, QueryResponse

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
        # Determine top_k and score_threshold explicitly and log them for debugging.
        top_k = request.top_k or settings.top_k_results
        # Use explicit None check so a provided 0.0 is respected if set intentionally.
        score_threshold = (
            request.similarity_threshold
            if request.similarity_threshold is not None
            else settings.similarity_threshold
        )

        logger.info(
            "Search called: query=%r, top_k=%s, request.similarity_threshold=%s, "
            "settings.similarity_threshold=%s, using_score_threshold=%s, filters=%s",
            request.query,
            top_k,
            request.similarity_threshold,
            settings.similarity_threshold,
            score_threshold,
            filters,
        )

        results = vector_store.search(
            query=request.query,
            top_k=top_k,
            score_threshold=score_threshold,
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
            detail=f"Search failed: {str(e)}",
        ) from e


@router.post(
    "/index",
    tags=["Indexing"],
    summary="Index documents",
    response_model=IndexResponse,
    status_code=status.HTTP_200_OK,
)
async def index_documents(documents: list[Document]):
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
            detail=f"Indexing failed: {str(e)}",
        ) from e


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
            detail=f"Failed to get collection info: {str(e)}",
        ) from e
