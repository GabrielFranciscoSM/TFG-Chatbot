"""Embeddings package: model wrappers and vector store integration."""

from rag_service.embeddings.embeddings import EmbeddingService, get_embedding_service
from rag_service.embeddings.store import VectorStoreService, get_vector_store

__all__ = [
    "EmbeddingService",
    "get_embedding_service",
    "VectorStoreService",
    "get_vector_store",
]
