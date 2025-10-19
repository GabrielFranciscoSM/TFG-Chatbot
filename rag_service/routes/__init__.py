"""Routes package for RAG service."""

from .files import router as files
from .general import router as general
from .search_index import router as search_index
from .subjects import router as subjects

__all__ = ["files", "general", "search_index", "subjects"]
