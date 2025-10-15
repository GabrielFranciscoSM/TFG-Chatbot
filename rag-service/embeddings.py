"""Embedding generation using Ollama."""

from langchain_ollama import OllamaEmbeddings
from typing import List
import logging

from rag_service.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating embeddings using Ollama."""
    
    def __init__(self):
        """Initialize Ollama embeddings."""
        ollama_url = f"http://{settings.ollama_host}:{settings.ollama_port}"
        
        logger.info(f"Initializing Ollama embeddings at {ollama_url}")
        logger.info(f"Using model: {settings.ollama_model}")
        
        self.embeddings = OllamaEmbeddings(
            base_url=ollama_url,
            model=settings.ollama_model,
        )
    
    def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding for a single query text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        try:
            embedding = self.embeddings.embed_query(text)
            logger.debug(f"Generated embedding for query of length {len(text)}")
            return embedding
        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            raise
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple documents.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            embeddings = self.embeddings.embed_documents(texts)
            logger.debug(f"Generated embeddings for {len(texts)} documents")
            return embeddings
        except Exception as e:
            logger.error(f"Error generating document embeddings: {e}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embedding vectors.
        
        Returns:
            Embedding dimension
        """
        return settings.embedding_dimension


# Global embedding service instance
_embedding_service: EmbeddingService | None = None


def get_embedding_service() -> EmbeddingService:
    """
    Get or create the global embedding service instance.
    
    Returns:
        EmbeddingService instance
    """
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
