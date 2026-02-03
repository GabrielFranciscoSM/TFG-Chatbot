# Chatbot Configuration

This document covers all configuration options for the Chatbot Service.

## Configuration System

The Chatbot Service uses `pydantic-settings` for type-safe configuration management. Settings are loaded from environment variables with sensible defaults for Docker Compose environments.

```python
# chatbot/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
```

## Environment Variables

### LLM Provider Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `LLM_PROVIDER` | string | `vllm` | LLM provider: `gemini`, `mistral`, or `vllm` |

```mermaid
flowchart TD
    Config[LLM_PROVIDER]
    
    Config -->|gemini| GeminiConfig[Gemini Settings]
    Config -->|mistral| MistralConfig[Mistral Settings]
    Config -->|vllm| VLLMConfig[vLLM Settings]
    
    GeminiConfig --> GKEY[GEMINI_API_KEY]
    GeminiConfig --> GMODEL[GEMINI_MODEL]
    
    MistralConfig --> MKEY[MISTRAL_API_KEY]
    MistralConfig --> MMODEL[MISTRAL_MODEL]
    
    VLLMConfig --> VHOST[VLLM_HOST]
    VLLMConfig --> VPORT[VLLM_MAIN_PORT]
    VLLMConfig --> VMODEL[MODEL_PATH]
```

### Gemini Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `GEMINI_API_KEY` | SecretStr | None | Google Gemini API key |
| `GEMINI_MODEL` | string | `gemini-2.5-flash` | Gemini model name |

**Example**:

```bash
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIzaSy...
GEMINI_MODEL=gemini-2.5-flash
```

### Mistral Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `MISTRAL_API_KEY` | SecretStr | None | Mistral AI API key |
| `MISTRAL_MODEL` | string | `mistral-large-latest` | Mistral model name |

**Example**:

```bash
LLM_PROVIDER=mistral
MISTRAL_API_KEY=...
MISTRAL_MODEL=mistral-large-latest
```

### vLLM Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `VLLM_HOST` | string | `vllm-openai` | vLLM service hostname |
| `VLLM_MAIN_PORT` | string | `8000` | vLLM service port |
| `MODEL_PATH` | string | `/models/HuggingFaceTB--SmolLM2-1.7B-Instruct` | Model path |

**Example**:

```bash
LLM_PROVIDER=vllm
VLLM_HOST=vllm-openai
VLLM_MAIN_PORT=8000
MODEL_PATH=/models/Qwen--Qwen2.5-1.5B-Instruct
```

**Computed Property**:

```python
@property
def vllm_url(self) -> str:
    return f"http://{self.vllm_host}:{self.vllm_main_port}/v1"
```

---

### Service URLs

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `RAG_SERVICE_URL` | string | `http://rag_service:8081` | RAG service base URL |
| `BACKEND_SERVICE_URL` | string | `http://backend:8000` | Backend service URL |

```mermaid
flowchart LR
    Chatbot[Chatbot :8080]
    
    Chatbot -->|RAG_SERVICE_URL| RAG[RAG Service :8081]
    Chatbot -->|BACKEND_SERVICE_URL| Backend[Backend :8000]
```

---

### MongoDB Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `MONGO_URI` | SecretStr | None | Full MongoDB connection URI |
| `MONGO_HOSTNAME` | string | None | MongoDB hostname |
| `MONGO_PORT` | string | `27017` | MongoDB port |
| `MONGO_ROOT_USERNAME` | string | None | MongoDB username |
| `MONGO_ROOT_PASSWORD` | SecretStr | None | MongoDB password |
| `MONGO_AUTH_DB` | string | None | Authentication database |
| `DB_NAME` | string | `tfg_chatbot` | Database name |

**URI Construction Logic**:

```python
def get_mongo_uri(self) -> str:
    # Priority 1: Direct URI
    if self.mongo_uri:
        return self.mongo_uri.get_secret_value()
    
    # Priority 2: Hostname with auth
    if self.mongo_hostname:
        if self.mongo_root_username and self.mongo_root_password:
            password = self.mongo_root_password.get_secret_value()
            if self.mongo_auth_db:
                return f"mongodb://{username}:{password}@{hostname}:{port}/?authSource={auth_db}"
            return f"mongodb://{username}:{password}@{hostname}:{port}"
        return f"mongodb://{hostname}:{port}"
    
    # Priority 3: Default
    return "mongodb://localhost:27017"
```

**Example** (Docker Compose):

```bash
MONGO_HOSTNAME=mongodb
MONGO_PORT=27017
MONGO_ROOT_USERNAME=admin
MONGO_ROOT_PASSWORD=secretpassword
MONGO_AUTH_DB=admin
DB_NAME=tfg_chatbot
```

**Example** (Cloud MongoDB):

```bash
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/tfg_chatbot
```

---

### Phoenix/OpenInference Observability

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `PHOENIX_ENABLED` | bool | `true` | Enable Phoenix tracing |
| `PHOENIX_HOST` | string | `phoenix` | Phoenix collector hostname |
| `PHOENIX_PORT` | string | `6006` | Phoenix collector port |
| `PHOENIX_PROJECT_NAME` | string | `tfg-chatbot` | Project name in Phoenix UI |

```mermaid
flowchart LR
    Chatbot[Chatbot Service]
    Phoenix[Phoenix Collector :6006]
    UI[Phoenix UI]
    
    Chatbot -->|OTLP/HTTP traces| Phoenix
    Phoenix --> UI
```

**Example**:

```bash
PHOENIX_ENABLED=true
PHOENIX_HOST=phoenix
PHOENIX_PORT=6006
PHOENIX_PROJECT_NAME=tfg-chatbot
```

**To disable observability**:

```bash
PHOENIX_ENABLED=false
```

---

### Difficulty Classifier Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `DIFFICULTY_CENTROIDS_PATH` | string | None | Path to trained centroids JSON |
| `DIFFICULTY_EMBEDDING_DIM` | int | `768` | Embedding dimension |
| `DIFFICULTY_USE_HEURISTICS` | bool | `true` | Enable heuristic fallback |

The difficulty classifier uses two methods:

1. **Heuristic-based** (fast, no latency) - Uses keyword/pattern matching
2. **Embedding-based** (more accurate) - Uses semantic similarity to centroids

**Example**:

```bash
DIFFICULTY_CENTROIDS_PATH=/app/data/difficulty_centroids.json
DIFFICULTY_EMBEDDING_DIM=768
DIFFICULTY_USE_HEURISTICS=true
```

---

## Complete Configuration Example

### Development (.env)

```bash
# =============================================================================
# LLM Configuration (Development - Gemini)
# =============================================================================
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIzaSy...your-key
GEMINI_MODEL=gemini-2.5-flash

# =============================================================================
# Service URLs
# =============================================================================
RAG_SERVICE_URL=http://localhost:8081
BACKEND_SERVICE_URL=http://localhost:8000

# =============================================================================
# MongoDB (Local)
# =============================================================================
MONGO_HOSTNAME=localhost
MONGO_PORT=27017
DB_NAME=tfg_chatbot

# =============================================================================
# Observability (Disabled for local dev)
# =============================================================================
PHOENIX_ENABLED=false

# =============================================================================
# Difficulty Classifier
# =============================================================================
DIFFICULTY_USE_HEURISTICS=true
```

### Production (Docker Compose)

```bash
# =============================================================================
# LLM Configuration (Production - vLLM)
# =============================================================================
LLM_PROVIDER=vllm
VLLM_HOST=vllm-openai
VLLM_MAIN_PORT=8000
MODEL_PATH=/models/Qwen--Qwen2.5-1.5B-Instruct

# =============================================================================
# Service URLs (Docker network)
# =============================================================================
RAG_SERVICE_URL=http://rag_service:8081
BACKEND_SERVICE_URL=http://backend:8000

# =============================================================================
# MongoDB (With authentication)
# =============================================================================
MONGO_HOSTNAME=mongodb
MONGO_PORT=27017
MONGO_ROOT_USERNAME=admin
MONGO_ROOT_PASSWORD=${MONGO_ROOT_PASSWORD}
MONGO_AUTH_DB=admin
DB_NAME=tfg_chatbot

# =============================================================================
# Observability (Enabled)
# =============================================================================
PHOENIX_ENABLED=true
PHOENIX_HOST=phoenix
PHOENIX_PORT=6006
PHOENIX_PROJECT_NAME=tfg-chatbot

# =============================================================================
# Difficulty Classifier
# =============================================================================
DIFFICULTY_CENTROIDS_PATH=/app/data/difficulty_centroids.json
DIFFICULTY_EMBEDDING_DIM=768
DIFFICULTY_USE_HEURISTICS=true
```

---

## Docker Compose Configuration

### Service Definition

```yaml
chatbot:
  build:
    context: .
    dockerfile: chatbot/Dockerfile
    args:
      INSTALL_DEV: "${INSTALL_DEV:-false}"
  ports:
    - "8080:8080"
  environment:
    - LLM_PROVIDER=${LLM_PROVIDER:-gemini}
    - GEMINI_API_KEY=${GEMINI_API_KEY}
    - GEMINI_MODEL=${GEMINI_MODEL:-gemini-2.5-flash}
    - RAG_SERVICE_URL=http://rag_service:8081
    - BACKEND_SERVICE_URL=http://backend:8000
    - MONGO_HOSTNAME=mongodb
    - MONGO_PORT=27017
    - MONGO_ROOT_USERNAME=${MONGO_ROOT_USERNAME}
    - MONGO_ROOT_PASSWORD=${MONGO_ROOT_PASSWORD}
    - MONGO_AUTH_DB=admin
    - DB_NAME=tfg_chatbot
    - PHOENIX_ENABLED=${PHOENIX_ENABLED:-true}
    - PHOENIX_HOST=phoenix
    - PHOENIX_PORT=6006
  depends_on:
    - mongodb
    - rag_service
    - phoenix
  volumes:
    - chatbot_storage:/app/chatbot/storage
  networks:
    - tfg-network
```

### Volume for Checkpoints

```yaml
volumes:
  chatbot_storage:
    driver: local
```

The checkpoint database (`checkpoints.db`) is stored in a Docker volume to persist conversation state across container restarts.

---

## Configuration Validation

### At Startup

The service validates configuration at startup:

```python
# Gemini provider requires API key
if settings.llm_provider == "gemini" and not settings.gemini_api_key:
    raise ValueError("GEMINI_API_KEY not found")

# Mistral provider requires API key
if settings.llm_provider == "mistral" and not settings.mistral_api_key:
    raise ValueError("MISTRAL_API_KEY not found")
```

### Health Check

Use the health endpoint to verify configuration:

```bash
curl http://localhost:8080/health
# {"message": "Hello World"}

curl http://localhost:8080/system/info
# {"version": "1.0.0", "llm_provider": "Gemini", "llm_model": "gemini-2.5-flash", "status": "operational"}
```

---

## Secret Management

### SecretStr Fields

Sensitive values use Pydantic's `SecretStr` to prevent accidental logging:

```python
gemini_api_key: SecretStr | None = None
mistral_api_key: SecretStr | None = None
mongo_uri: SecretStr | None = None
mongo_root_password: SecretStr | None = None
```

### Accessing Secret Values

```python
# Safe access methods
def get_gemini_api_key(self) -> str | None:
    return self.gemini_api_key.get_secret_value() if self.gemini_api_key else None
```

### Best Practices

1. **Never commit secrets** - Use `.env` files (gitignored)
2. **Use environment variables** - In CI/CD and production
3. **Docker secrets** - For production deployments
4. **Check logs** - Ensure secrets aren't logged

---

## Configuration Hierarchy

```mermaid
flowchart TD
    ENV[Environment Variables]
    DOTENV[.env File]
    DEFAULTS[Default Values]
    
    ENV --> Settings
    DOTENV --> Settings
    DEFAULTS --> Settings
    
    Settings --> App[Application]
    
    subgraph Priority
        P1[1. Environment Variables]
        P2[2. .env File]
        P3[3. Defaults]
    end
```

**Resolution Order**:
1. Environment variables (highest priority)
2. `.env` file values
3. Default values in `Settings` class

---

## Related Documentation

- [Architecture](architecture.md) - System overview
- [Deployment](deployment.md) - Production configuration
- [Development](development.md) - Local setup
