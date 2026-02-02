---
layout: default
title: Configuration
parent: Developer Guide
nav_order: 5
---

# Configuration

Environment variables and configuration options for the TFG-Chatbot project.

---

## Environment Variables

All configuration is done through environment variables, typically stored in a `.env` file.

### LLM Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `gemini` | LLM provider: `gemini`, `mistral`, or `vllm` |
| `GOOGLE_API_KEY` | - | Gemini API key (required if provider=gemini) |
| `MISTRAL_API_KEY` | - | Mistral API key (required if provider=mistral) |
| `VLLM_API_URL` | `http://localhost:8085/v1` | vLLM endpoint URL |
| `LLM_MODEL` | `gemini-2.0-flash` | Model name for inference |
| `LLM_TEMPERATURE` | `0.7` | Generation temperature |
| `LLM_MAX_TOKENS` | `2048` | Maximum output tokens |

### Database Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `MONGO_HOSTNAME` | `localhost` | MongoDB hostname |
| `MONGO_PORT` | `27017` | MongoDB port |
| `MONGO_ROOT_USERNAME` | `root` | MongoDB admin username |
| `MONGO_ROOT_PASSWORD` | `example` | MongoDB admin password |
| `MONGO_DATABASE` | `tfg_chatbot` | Database name |

### Vector Store Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `QDRANT_URL` | `http://localhost:6333` | Qdrant server URL |
| `QDRANT_COLLECTION` | `documents` | Default collection name |
| `OLLAMA_URL` | `http://localhost:11434` | Ollama server URL |
| `EMBEDDING_MODEL` | `nomic-embed-text` | Embedding model name |
| `EMBEDDING_DIMENSION` | `768` | Vector dimension |

### Service URLs

| Variable | Default | Description |
|----------|---------|-------------|
| `CHATBOT_SERVICE_URL` | `http://localhost:8080` | Chatbot service URL |
| `RAG_SERVICE_URL` | `http://localhost:8081` | RAG service URL |
| `BACKEND_URL` | `http://localhost:8000` | Backend gateway URL |

{: .note }
Inside containers, use service names instead of `localhost` (e.g., `http://chatbot:8080`).

### Security

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | - | JWT signing key (min 32 chars) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | JWT token expiration (24h) |
| `ALGORITHM` | `HS256` | JWT algorithm |

---

## Example `.env` File

```bash
# ============================================================================
# TFG-Chatbot Environment Configuration
# ============================================================================

# LLM Provider Configuration
LLM_PROVIDER=gemini
GOOGLE_API_KEY=your-google-api-key-here
LLM_MODEL=gemini-2.0-flash

# MongoDB
MONGO_ROOT_USERNAME=root
MONGO_ROOT_PASSWORD=example
MONGO_HOSTNAME=localhost
MONGO_PORT=27017
MONGO_DATABASE=tfg_chatbot

# Vector Store
QDRANT_URL=http://localhost:6333
OLLAMA_URL=http://localhost:11434
EMBEDDING_MODEL=nomic-embed-text

# Service URLs (local development)
CHATBOT_SERVICE_URL=http://localhost:8080
RAG_SERVICE_URL=http://localhost:8081

# Security
SECRET_KEY=your-super-secret-key-at-least-32-characters-long

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Development
DEBUG=false
```

---

## Service-Specific Configuration

Each service has its own `config.py` using Pydantic Settings:

### Backend Configuration

```python
# backend/config.py
class Settings:
    mongo_hostname: str = "localhost"
    mongo_port: int = 27017
    mongo_root_username: str = "root"
    mongo_root_password: str = "example"
    mongo_database: str = "tfg_chatbot"
    
    secret_key: str
    access_token_expire_minutes: int = 1440
    
    chatbot_service_url: str = "http://localhost:8080"
```

### Chatbot Configuration

```python
# chatbot/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    llm_provider: str = "gemini"
    google_api_key: str | None = None
    mistral_api_key: str | None = None
    vllm_api_url: str = "http://localhost:8085/v1"
    
    rag_service_url: str = "http://localhost:8081"
    
    class Config:
        env_file = ".env"
```

### RAG Service Configuration

```python
# rag_service/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    qdrant_url: str = "http://localhost:6333"
    ollama_url: str = "http://localhost:11434"
    embedding_model: str = "nomic-embed-text"
    embedding_dimension: int = 768
    
    class Config:
        env_file = ".env"
```

---

## Docker Compose Configuration

The `docker-compose.yml` sets environment variables for containers:

```yaml
services:
  backend:
    environment:
      - MONGO_HOSTNAME=mongo
      - CHATBOT_SERVICE_URL=http://chatbot:8080
      
  chatbot:
    environment:
      - RAG_SERVICE_URL=http://rag_service:8081
      - LLM_PROVIDER=${LLM_PROVIDER:-gemini}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
```

{: .important }
Container hostnames use service names (`mongo`, `chatbot`, `rag_service`) instead of `localhost`.

---

## Configuration Precedence

Settings are loaded in this order (later overrides earlier):

1. **Default values** in `config.py`
2. **`.env` file** in project root
3. **Environment variables** set in shell
4. **Docker Compose** environment section

---

## Logging Configuration

### Log Levels

| Level | Description |
|-------|-------------|
| `DEBUG` | Detailed diagnostic information |
| `INFO` | General operational messages |
| `WARNING` | Warning messages |
| `ERROR` | Error messages |
| `CRITICAL` | Critical errors |

### JSON Logging

Set `LOG_FORMAT=json` for structured logging:

```json
{
  "timestamp": "2024-01-31T12:00:00Z",
  "level": "INFO",
  "message": "Request processed",
  "service": "backend",
  "request_id": "abc123"
}
```

---

## Production Configuration

For production deployments:

```bash
# Production .env example
LLM_PROVIDER=vllm
VLLM_API_URL=http://vllm-server:8085/v1

MONGO_ROOT_PASSWORD=strong-production-password
SECRET_KEY=production-secret-key-64-characters-minimum

LOG_LEVEL=WARNING
LOG_FORMAT=json
DEBUG=false
```

{: .warning }
Never commit `.env` files with real credentials to version control.
