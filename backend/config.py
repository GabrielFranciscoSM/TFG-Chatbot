from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Backend gateway configuration settings."""

    chatbot_service_url: str = "http://chatbot:8080"
    rag_service_url: str = "http://rag_service:8081"
    chatbot_timeout: float = 120.0  # Timeout for LLM requests (can be slow)

    # MongoDB configuration
    mongo_uri: SecretStr | None = None
    mongo_hostname: str | None = None
    mongo_port: str = "27017"
    mongo_root_username: str | None = None
    mongo_root_password: SecretStr | None = None
    mongo_auth_db: str | None = None
    db_name: str = "tfg_chatbot"

    # Auth configuration
    # IMPORTANT: Override SECRET_KEY in production! Never use the default.
    secret_key: SecretStr = SecretStr("dev-only-secret-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

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
