"""Configuration for RAG service."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """RAG Service configuration settings."""

    # Qdrant configuration
    qdrant_host: str = "qdrant"
    qdrant_port: int = 6333
    qdrant_collection_name: str = "academic_documents"

    # Ollama configuration
    ollama_host: str = "ollama"
    # Ollama's API server port. Use 11434 by default for internal communication
    # (11435 is usually the host mapped port).
    ollama_port: int = 11434
    ollama_model: str = "nomic-embed-text"

    # RAG parameters
    embedding_dimension: int = 768  # nomic-embed-text dimension
    top_k_results: int = 5
    similarity_threshold: float = 0.5

    # Chunking parameters
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # API configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8081
    cors_origins: list[str] = ["*"]

    # Documents storage
    documents_path: str = "/app/documents"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
