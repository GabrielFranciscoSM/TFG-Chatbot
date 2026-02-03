# Embedding Service

This document describes the embedding generation system using Ollama for text vectorization.

## Overview

The RAG service uses Ollama to generate dense vector embeddings from text. These embeddings enable semantic similarity search in the Qdrant vector database.

```mermaid
graph LR
    subgraph "RAG Service"
        ES[EmbeddingService]
    end
    
    subgraph "Ollama :11434"
        API[/api/embeddings]
        Model[nomic-embed-text]
    end
    
    ES -->|POST| API
    API --> Model
    Model -->|768-dim vector| ES
```

## EmbeddingService Class

Located in `embeddings/embeddings.py`:

```python
class EmbeddingService:
    """Service for generating embeddings using Ollama."""
    
    def embed_query(self, text: str) -> list[float]:
        """Generate embedding for a single query."""
        
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple documents."""
        
    def get_embedding_dimension(self) -> int:
        """Get the embedding vector dimension."""
```

### Singleton Pattern

The service uses a singleton pattern for connection reuse:

```python
_embedding_service: EmbeddingService | None = None

def get_embedding_service() -> EmbeddingService:
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
```

---

## Embedding Model

### nomic-embed-text

Default model for the RAG service:

| Property | Value |
|----------|-------|
| **Model** | `nomic-embed-text` |
| **Dimensions** | 768 |
| **Context Length** | 8192 tokens |
| **Use Case** | General-purpose text embeddings |

**Why nomic-embed-text?**
- Good balance of quality and speed
- Efficient for document retrieval
- Runs well on CPU (no GPU required)
- Open source and locally hosted

### Model Installation

```bash
# Pull the model in Ollama
docker exec ollama ollama pull nomic-embed-text

# Verify installation
docker exec ollama ollama list
```

---

## Configuration

Environment variables for embedding service:

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_HOST` | `ollama` | Ollama server hostname |
| `OLLAMA_PORT` | `11434` | Ollama API port |
| `OLLAMA_MODEL` | `nomic-embed-text` | Embedding model name |
| `EMBEDDING_DIMENSION` | `768` | Vector dimension |

```python
# config.py
class Settings(BaseSettings):
    ollama_host: str = "ollama"
    ollama_port: int = 11434
    ollama_model: str = "nomic-embed-text"
    embedding_dimension: int = 768
```

---

## Usage

### Embed a Single Query

```python
from rag_service.embeddings import get_embedding_service

embedding_service = get_embedding_service()

# Generate query embedding
query = "What is fuzzy logic?"
embedding = embedding_service.embed_query(query)

print(f"Dimension: {len(embedding)}")  # 768
print(f"First 5 values: {embedding[:5]}")
```

### Embed Multiple Documents

```python
documents = [
    "Fuzzy logic is a form of many-valued logic.",
    "Machine learning uses algorithms to learn from data.",
    "Docker containers provide isolated environments."
]

embeddings = embedding_service.embed_documents(documents)

print(f"Number of embeddings: {len(embeddings)}")  # 3
print(f"Each dimension: {len(embeddings[0])}")     # 768
```

---

## LangChain Integration

The service uses `langchain-ollama` for Ollama integration:

```python
from langchain_ollama import OllamaEmbeddings

class EmbeddingService:
    def __init__(self):
        ollama_url = f"http://{settings.ollama_host}:{settings.ollama_port}"
        
        self.embeddings = OllamaEmbeddings(
            base_url=ollama_url,
            model=settings.ollama_model,
        )
```

### Direct API Usage

Alternatively, use the Ollama API directly:

```bash
curl http://localhost:11434/api/embeddings \
  -d '{
    "model": "nomic-embed-text",
    "prompt": "What is Docker?"
  }'
```

Response:
```json
{
  "embedding": [0.123, -0.456, 0.789, ...]
}
```

---

## Performance Considerations

### Batch Processing

For large document sets, use batch embedding:

```python
# Efficient: One API call for multiple documents
embeddings = embedding_service.embed_documents(all_texts)

# Inefficient: Multiple API calls
for text in all_texts:
    embedding = embedding_service.embed_query(text)  # Slow!
```

### Caching

Consider caching embeddings for frequently used queries:

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_embed_query(text: str) -> tuple:
    embedding = embedding_service.embed_query(text)
    return tuple(embedding)  # Convert to hashable
```

### Connection Pooling

The singleton pattern ensures a single connection:

```python
# Good: Reuses connection
store1 = get_embedding_service()
store2 = get_embedding_service()
assert store1 is store2  # Same instance
```

---

## Alternative Models

### Changing the Model

To use a different embedding model:

1. Pull the model:
   ```bash
   docker exec ollama ollama pull mxbai-embed-large
   ```

2. Update configuration:
   ```bash
   export OLLAMA_MODEL=mxbai-embed-large
   export EMBEDDING_DIMENSION=1024
   ```

3. **Important**: Delete and recreate Qdrant collection (dimension mismatch):
   ```python
   vector_store.delete_collection()
   # Collection will be recreated with new dimension
   ```

### Model Comparison

| Model | Dimensions | Speed | Quality |
|-------|------------|-------|---------|
| `nomic-embed-text` | 768 | Fast | Good |
| `mxbai-embed-large` | 1024 | Medium | Better |
| `all-minilm` | 384 | Very Fast | Basic |

---

## Error Handling

### Connection Errors

```python
try:
    embedding = embedding_service.embed_query(text)
except Exception as e:
    logger.error(f"Embedding failed: {e}")
    # Handle Ollama connection issues
```

### Common Issues

| Error | Cause | Solution |
|-------|-------|----------|
| `Connection refused` | Ollama not running | Start Ollama container |
| `Model not found` | Model not pulled | Run `ollama pull nomic-embed-text` |
| `Timeout` | Large text or slow GPU | Reduce chunk size |

### Health Check

Verify Ollama is working:

```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Test embedding
curl http://localhost:11434/api/embeddings \
  -d '{"model": "nomic-embed-text", "prompt": "test"}'
```

---

## Monitoring

### Logging

The service logs embedding operations:

```python
logger.info(f"Initializing Ollama embeddings at {ollama_url}")
logger.info(f"Using model: {settings.ollama_model}")
logger.debug(f"Generated embedding for query of length {len(text)}")
logger.debug(f"Generated embeddings for {len(texts)} documents")
```

### Metrics

Track embedding performance:

```python
import time

start = time.time()
embeddings = embedding_service.embed_documents(texts)
duration = time.time() - start

logger.info(f"Embedded {len(texts)} docs in {duration:.2f}s")
```

---

## Testing

### Unit Tests

```python
# tests/test_embeddings_service.py

def test_embed_query():
    service = get_embedding_service()
    embedding = service.embed_query("test text")
    
    assert len(embedding) == 768
    assert all(isinstance(v, float) for v in embedding)

def test_embed_documents():
    service = get_embedding_service()
    texts = ["doc 1", "doc 2"]
    embeddings = service.embed_documents(texts)
    
    assert len(embeddings) == 2
    assert all(len(e) == 768 for e in embeddings)
```

### Mock for Testing

```python
from unittest.mock import Mock, patch

@patch('rag_service.embeddings.embeddings.OllamaEmbeddings')
def test_with_mock(mock_ollama):
    mock_ollama.return_value.embed_query.return_value = [0.1] * 768
    
    service = EmbeddingService()
    result = service.embed_query("test")
    
    assert len(result) == 768
```

---

## Related Documentation

- [Vector Store](vector-store.md) - Qdrant integration
- [Architecture](architecture.md) - System design
- [Configuration](configuration.md) - Environment variables
