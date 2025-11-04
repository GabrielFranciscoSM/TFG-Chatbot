"""Routes package for RAG service."""

from rag_service.routes.files import router as files
from rag_service.routes.general import router as general
from rag_service.routes.search_index import router as search_index
from rag_service.routes.subjects import router as subjects

__all__ = ["files", "general", "search_index", "subjects"]
