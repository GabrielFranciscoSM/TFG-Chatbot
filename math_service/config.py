"""Configuration for Math service."""

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Math Service configuration settings."""

    # MongoDB configuration
    mongo_uri: SecretStr | None = None
    mongo_hostname: str | None = None
    mongo_port: str = "27017"
    mongo_root_username: str | None = None
    mongo_root_password: SecretStr | None = None
    mongo_auth_db: str | None = None
    db_name: str = "tfg_chatbot"

    # Ollama configuration
    ollama_host: str = "ollama"
    ollama_port: int = 11434
    ollama_model: str = "nomic-embed-text"

    # RAG Service
    rag_service_url: str = "http://rag_service:8081"

    # API configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8083
    cors_origins: list[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

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
