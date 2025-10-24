"""Embeddings package: model wrappers and vector store integration."""

from .embeddings import EmbeddingService, get_embedding_service
from .store import VectorStoreService, get_vector_store

__all__ = ["EmbeddingService", "get_embedding_service", "VectorStoreService", "get_vector_store"]
