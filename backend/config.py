"""Backend configuration settings."""

import os

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings for backend components."""

    # URL for the external RAG service. When running via docker-compose the
    # backend and rag_service share a network, so use the compose service name
    # (`rag_service`) as the default hostname rather than localhost. Override
    # with the RAG_SERVICE_URL env var if needed.
    rag_service_url: str = os.getenv("RAG_SERVICE_URL", "http://rag_service:8081")

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
    )


settings = Settings()
