"""Chatbot configuration settings."""

from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings for chatbot components."""

    # RAG Service configuration
    rag_service_url: str = "http://rag_service:8081"

    # LLM Provider configuration
    llm_provider: Literal["vllm", "gemini", "mistral"] = "vllm"

    # vLLM configuration
    vllm_host: str = "vllm-openai"
    vllm_main_port: str = "8000"
    model_path: str = "/models/HuggingFaceTB--SmolLM2-1.7B-Instruct"

    # Gemini configuration (SecretStr to avoid logging API key)
    gemini_api_key: SecretStr | None = None
    gemini_model: str = "gemini-2.5-flash"

    # Mistral configuration (SecretStr to avoid logging API key)
    mistral_api_key: SecretStr | None = None
    mistral_model: str = "mistral-large-latest"

    # MongoDB configuration
    mongo_uri: SecretStr | None = None
    mongo_hostname: str | None = None
    mongo_port: str = "27017"
    mongo_root_username: str | None = None
    mongo_root_password: SecretStr | None = None
    mongo_auth_db: str | None = None
    db_name: str = "tfg_chatbot"

    # Phoenix/OpenInference observability configuration
    phoenix_enabled: bool = True
    phoenix_host: str = "phoenix"
    phoenix_port: str = "6006"
    phoenix_project_name: str = "tfg-chatbot"

    # Difficulty classifier configuration
    difficulty_centroids_path: str | None = None
    difficulty_embedding_dim: int = 768
    difficulty_use_heuristics: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def vllm_url(self) -> str:
        """Construct vLLM API URL."""
        return f"http://{self.vllm_host}:{self.vllm_main_port}/v1"

    def get_gemini_api_key(self) -> str | None:
        """Get Gemini API key value safely."""
        return self.gemini_api_key.get_secret_value() if self.gemini_api_key else None

    def get_mistral_api_key(self) -> str | None:
        """Get Mistral API key value safely."""
        return self.mistral_api_key.get_secret_value() if self.mistral_api_key else None

    def get_mongo_uri(self) -> str:
        """Construct MongoDB URI from configuration."""
        if self.mongo_uri:
            return self.mongo_uri.get_secret_value()

        if self.mongo_hostname:
            if self.mongo_root_username and self.mongo_root_password:
                password = self.mongo_root_password.get_secret_value()
                if self.mongo_auth_db:
                    return f"mongodb://{self.mongo_root_username}:{password}@{self.mongo_hostname}:{self.mongo_port}/?authSource={self.mongo_auth_db}"
                return f"mongodb://{self.mongo_root_username}:{password}@{self.mongo_hostname}:{self.mongo_port}"
            return f"mongodb://{self.mongo_hostname}:{self.mongo_port}"

        return "mongodb://localhost:27017"


settings = Settings()
