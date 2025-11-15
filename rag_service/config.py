"""Configuration for RAG service."""

import os

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """RAG Service configuration settings."""

    # Qdrant configuration
    qdrant_host: str = os.getenv("QDRANT_HOST", "qdrant")
    qdrant_port: int = int(os.getenv("QDRANT_PORT", "6333"))
    qdrant_collection_name: str = os.getenv("QDRANT_COLLECTION", "academic_documents")

    # Ollama configuration
    ollama_host: str = os.getenv("OLLAMA_HOST", "ollama")
    ollama_port: int = int(os.getenv("OLLAMA_PORT", "11434"))
    ollama_model: str = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")

    # RAG parameters
    embedding_dimension: int = 768  # nomic-embed-text dimension
    top_k_results: int = int(os.getenv("RAG_TOP_K", "5"))
    similarity_threshold: float = float(os.getenv("RAG_SIMILARITY_THRESHOLD", "0.5"))

    # Chunking parameters
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "1000"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "200"))

    # API configuration
    api_host: str = os.getenv("RAG_API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("RAG_API_PORT", "8081"))

    # Documents storage
    documents_path: str = os.getenv("DOCUMENTS_PATH", "/app/documents")

    # In pydantic v2 use `model_config` to set env_file and extra behaviour.
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",  # ignore unrelated environment variables
    )


settings = Settings()
