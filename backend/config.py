"""Backend configuration settings."""

import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """Settings for backend components."""

    # URL for the external RAG service (default to local rag_service)
    rag_service_url: str = os.getenv("RAG_SERVICE_URL", "http://localhost:8081")

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
    )


settings = Settings()
