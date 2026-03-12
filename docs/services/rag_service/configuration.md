# RAG Service Configuration

This document describes all configuration options for the RAG service.

## Overview

The RAG service uses `pydantic-settings` for type-safe configuration with environment variable support.

```python
# config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
```

---

## Environment Variables

### Qdrant Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `QDRANT_HOST` | string | `qdrant` | Qdrant server hostname |
| `QDRANT_PORT` | int | `6333` | Qdrant server port |
| `QDRANT_COLLECTION_NAME` | string | `academic_documents` | Collection name |

**Example:**
```bash
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=my_documents
```

### Ollama Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `OLLAMA_HOST` | string | `ollama` | Ollama server hostname |
| `OLLAMA_PORT` | int | `11434` | Ollama API port |
| `OLLAMA_MODEL` | string | `nomic-embed-text` | Embedding model |

**Example:**
```bash
OLLAMA_HOST=localhost
OLLAMA_PORT=11434
OLLAMA_MODEL=nomic-embed-text
```

### RAG Parameters

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `EMBEDDING_DIMENSION` | int | `768` | Vector dimension (must match model) |
| `TOP_K_RESULTS` | int | `5` | Default search results count |
| `SIMILARITY_THRESHOLD` | float | `0.5` | Minimum similarity score (0-1) |

**Example:**
```bash
EMBEDDING_DIMENSION=768
TOP_K_RESULTS=10
SIMILARITY_THRESHOLD=0.6
```

### Chunking Parameters

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `CHUNK_SIZE` | int | `1000` | Maximum characters per chunk |
| `CHUNK_OVERLAP` | int | `200` | Overlap between consecutive chunks |

**Example:**
```bash
CHUNK_SIZE=500
CHUNK_OVERLAP=100
```

### API Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `API_HOST` | string | `0.0.0.0` | API bind address |
| `API_PORT` | int | `8081` | API port |
| `CORS_ORIGINS` | list | `["*"]` | Allowed CORS origins |

**Example:**
```bash
API_HOST=0.0.0.0
API_PORT=8081
CORS_ORIGINS=["http://localhost:5173"]
```

### Storage Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `DOCUMENTS_PATH` | string | `/app/documents` | Documents directory |

**Example:**
```bash
DOCUMENTS_PATH=/data/documents
```

---

## Configuration Class

Full settings class definition:

```python
class Settings(BaseSettings):
    """RAG Service configuration settings."""
    
    # Qdrant configuration
    qdrant_host: str = "qdrant"
    qdrant_port: int = 6333
    qdrant_collection_name: str = "academic_documents"
    
    # Ollama configuration
    ollama_host: str = "ollama"
    ollama_port: int = 11434
    ollama_model: str = "nomic-embed-text"
    
    # RAG parameters
    embedding_dimension: int = 768
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
```

---

## Environment Files

### Development (.env)

```bash
# Qdrant (local)
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Ollama (local)
OLLAMA_HOST=localhost
OLLAMA_PORT=11434

# Development settings
DOCUMENTS_PATH=./documents
TOP_K_RESULTS=10
SIMILARITY_THRESHOLD=0.4
```

### Docker (.env.docker)

```bash
# Qdrant (container)
QDRANT_HOST=qdrant
QDRANT_PORT=6333

# Ollama (container)
OLLAMA_HOST=ollama
OLLAMA_PORT=11434

# Production settings
DOCUMENTS_PATH=/app/documents
TOP_K_RESULTS=5
SIMILARITY_THRESHOLD=0.5
```

### Example File (.env.example)

```bash
# ===========================================
# RAG Service Configuration
# ===========================================

# Qdrant Vector Database
QDRANT_HOST=qdrant
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=academic_documents

# Ollama Embedding Service
OLLAMA_HOST=ollama
OLLAMA_PORT=11434
OLLAMA_MODEL=nomic-embed-text

# Embedding Configuration
EMBEDDING_DIMENSION=768

# Search Parameters
TOP_K_RESULTS=5
SIMILARITY_THRESHOLD=0.5

# Chunking Parameters
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# API Server
API_HOST=0.0.0.0
API_PORT=8081
CORS_ORIGINS=["*"]

# Document Storage
DOCUMENTS_PATH=/app/documents
```

---

## Docker Compose Integration

### Service Definition

```yaml
rag_service:
  build:
    context: .
    dockerfile: ./rag_service/Dockerfile
  container_name: rag_service
  environment:
    - QDRANT_HOST=qdrant
    - QDRANT_PORT=6333
    - OLLAMA_HOST=ollama
    - OLLAMA_PORT=11434
    - DOCUMENTS_PATH=/app/documents
  ports:
    - "8081:8081"
  volumes:
    - ./rag_service/documents:/app/documents
  depends_on:
    - qdrant
    - ollama
```

### Dependent Services

```yaml
qdrant:
  image: qdrant/qdrant:latest
  ports:
    - "6333:6333"
  volumes:
    - qdrant_storage:/qdrant/storage

ollama:
  image: ollama/ollama:latest
  ports:
    - "11435:11434"
  volumes:
    - ollama_models:/root/.ollama
```

---

## Configuration by Environment

### Local Development

```bash
# Start dependencies
docker compose up -d qdrant ollama

# Run service locally
cd rag_service
export QDRANT_HOST=localhost
export OLLAMA_HOST=localhost
uvicorn rag_service.api:app --reload --port 8081
```

### Docker Development

```bash
# Use docker-compose defaults
docker compose up -d rag_service
```

### Production

```bash
# Production settings
export SIMILARITY_THRESHOLD=0.6
export TOP_K_RESULTS=5
export CHUNK_SIZE=800

# Or use .env file
cp .env.production .env
docker compose -f docker-compose.prod.yml up -d
```

---

## Tuning Guidelines

### Embedding Model Selection

| Model | Dimensions | `EMBEDDING_DIMENSION` |
|-------|------------|----------------------|
| `nomic-embed-text` | 768 | `768` |
| `mxbai-embed-large` | 1024 | `1024` |
| `all-minilm` | 384 | `384` |

⚠️ **Important**: Changing `EMBEDDING_DIMENSION` requires recreating the Qdrant collection.

### Chunking Strategy

| Document Type | `CHUNK_SIZE` | `CHUNK_OVERLAP` |
|---------------|--------------|-----------------|
| Short notes | 500 | 50 |
| Lecture slides | 800 | 100 |
| Textbook chapters | 1000 | 200 |
| Code documentation | 1200 | 150 |

### Search Quality

| Use Case | `TOP_K_RESULTS` | `SIMILARITY_THRESHOLD` |
|----------|-----------------|------------------------|
| Precise answers | 3-5 | 0.7-0.8 |
| Exploration | 10-15 | 0.4-0.5 |
| Comprehensive | 20+ | 0.3 |

---

## Validation

### Check Current Configuration

```python
from rag_service.config import settings

print(f"Qdrant: {settings.qdrant_host}:{settings.qdrant_port}")
print(f"Ollama: {settings.ollama_host}:{settings.ollama_port}")
print(f"Model: {settings.ollama_model}")
print(f"Chunk size: {settings.chunk_size}")
```

### Health Check Verification

```bash
# Check service health
curl http://localhost:8081/health

# Response shows configuration in action
{
  "status": "healthy",
  "qdrant_connected": true,
  "collection": {
    "name": "academic_documents",  # QDRANT_COLLECTION_NAME
    "points_count": 156
  }
}
```

---

## Troubleshooting

### Connection Issues

| Error | Check | Solution |
|-------|-------|----------|
| Qdrant connection refused | `QDRANT_HOST`, `QDRANT_PORT` | Verify Qdrant is running |
| Ollama connection failed | `OLLAMA_HOST`, `OLLAMA_PORT` | Check Ollama container |
| Model not found | `OLLAMA_MODEL` | Pull model: `ollama pull nomic-embed-text` |

### Dimension Mismatch

```
Error: Vector dimension mismatch
```

**Solution:**
1. Delete existing collection
2. Update `EMBEDDING_DIMENSION` to match model
3. Re-index documents

### CORS Errors

```bash
# Allow specific origins
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]

# Or allow all (development only)
CORS_ORIGINS=["*"]
```

---

## Related Documentation

- [Architecture](architecture.md) - System design
- [Development](development.md) - Local setup
- [Deployment](deployment.md) - Production config
