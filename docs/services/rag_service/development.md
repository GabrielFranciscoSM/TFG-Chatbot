# RAG Service Development

This document covers local development setup, testing, and debugging for the RAG service.

## Prerequisites

- Python 3.12+
- Docker (for Qdrant and Ollama)
- `uv` or `pip` for package management

---

## Local Setup

### 1. Start Dependencies

```bash
# Start Qdrant and Ollama
docker compose up -d qdrant ollama

# Initialize embedding model
docker exec ollama ollama pull nomic-embed-text

# Verify services
curl http://localhost:6333/healthz     # Qdrant
curl http://localhost:11434/api/tags   # Ollama
```

### 2. Install Python Dependencies

```bash
cd rag_service

# Using uv (recommended)
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# Or using pip
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 3. Configure Environment

```bash
# Create .env file
cat > .env << EOF
QDRANT_HOST=localhost
QDRANT_PORT=6333
OLLAMA_HOST=localhost
OLLAMA_PORT=11434
DOCUMENTS_PATH=./documents
EOF
```

### 4. Run the Service

```bash
# Development mode with auto-reload
uvicorn rag_service.api:app --reload --port 8081

# Or using the module
python -m rag_service
```

### 5. Verify Installation

```bash
# Health check
curl http://localhost:8081/health

# API info
curl http://localhost:8081/
```

---

## Project Structure

```
rag_service/
├── api.py                    # FastAPI application entry point
├── config.py                 # Pydantic settings
├── models.py                 # Request/response models
├── logging_config.py         # Structured logging
├── __main__.py               # Module entry point
├── pyproject.toml            # Dependencies
│
├── routes/                   # API endpoints
│   ├── general.py            # /, /health
│   ├── search_index.py       # /search, /index
│   ├── files.py              # /files, /upload
│   └── subjects.py           # /subjects
│
├── documents/                # Document processing
│   ├── file_loader.py        # Load PDF, TXT, MD
│   ├── document_processor.py # Text chunking
│   └── file_utils.py         # File system ops
│
├── embeddings/               # Vector operations
│   ├── embeddings.py         # Ollama embeddings
│   └── store.py              # Qdrant vector store
│
├── tests/                    # Test suite
│   ├── conftest.py           # Fixtures
│   ├── test_*.py             # Unit tests
│   └── test_integration.py   # Integration tests
│
└── documents/                # Sample documents
```

---

## Development Workflow

### Running Tests

```bash
cd rag_service

# All tests
pytest tests/ -v

# Unit tests only (no external services)
pytest tests/ -m "not integration" -v

# Integration tests (requires Qdrant/Ollama)
pytest tests/ -m integration -v

# With coverage
pytest tests/ -v --cov=. --cov-report=html
```

### Test Markers

```python
# pytest.ini
[pytest]
markers =
    unit: Unit tests (no external dependencies)
    integration: Integration tests (require external services)
```

### Code Quality

```bash
# Linting
ruff check .

# Formatting
black .
isort .

# Type checking
mypy .
```

---

## Testing Strategies

### Unit Tests

Test individual components without external services:

```python
# tests/test_document_processor.py

def test_chunk_document():
    processor = DocumentProcessor(chunk_size=100, chunk_overlap=20)
    doc = Document(content="x" * 500, metadata=sample_metadata)
    
    chunks = processor.chunk_document(doc)
    
    assert len(chunks) > 1
    assert all(len(c.content) <= 120 for c in chunks)  # Allow overlap
    assert all(c.metadata.chunk_id is not None for c in chunks)
```

### Mock External Services

```python
# tests/test_search.py
from unittest.mock import Mock, patch

@patch('rag_service.embeddings.store.QdrantClient')
@patch('rag_service.embeddings.embeddings.OllamaEmbeddings')
def test_search_with_mocks(mock_ollama, mock_qdrant):
    # Configure mocks
    mock_ollama.return_value.embed_query.return_value = [0.1] * 768
    mock_qdrant.return_value.query_points.return_value = Mock(points=[])
    
    # Test search
    store = VectorStoreService()
    results = store.search("test query")
    
    assert results == []
```

### Integration Tests

Test with real external services:

```python
# tests/test_integration.py
import pytest

@pytest.mark.integration
def test_full_indexing_pipeline():
    """Test complete indexing and search flow."""
    store = get_vector_store()
    
    # Index a document
    doc = Document(
        content="Docker is a containerization platform.",
        metadata=DocumentMetadata(
            asignatura="iv",
            tipo_documento="teoria"
        )
    )
    indexed = store.index_documents([doc])
    assert indexed > 0
    
    # Search for it
    results = store.search("What is Docker?")
    assert len(results) > 0
    assert "Docker" in results[0].content
```

### Fixtures

```python
# tests/conftest.py
import pytest
from rag_service.models import Document, DocumentMetadata

@pytest.fixture
def sample_metadata():
    return DocumentMetadata(
        asignatura="test-subject",
        tipo_documento="test-type"
    )

@pytest.fixture
def sample_document(sample_metadata):
    return Document(
        content="Test document content for unit testing.",
        metadata=sample_metadata,
        doc_id="test-doc"
    )

@pytest.fixture
def temp_documents_dir(tmp_path):
    """Create temporary documents directory structure."""
    docs = tmp_path / "documents"
    (docs / "test-subject" / "test-type").mkdir(parents=True)
    return docs
```

---

## Debugging

### Enable Debug Logging

```python
# logging_config.py
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("rag_service")
logger.setLevel(logging.DEBUG)
```

### Debug Endpoints

```bash
# Check collection info
curl http://localhost:8081/collection/info

# List all files
curl http://localhost:8081/files

# Check subjects
curl http://localhost:8081/subjects
```

### Interactive Debugging

```python
# Launch Python REPL with service loaded
python -c "
from rag_service.embeddings.store import get_vector_store
from rag_service.config import settings

print(f'Qdrant: {settings.qdrant_host}:{settings.qdrant_port}')

store = get_vector_store()
info = store.get_collection_info()
print(f'Collection: {info}')
"
```

### Debug in VSCode

```json
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "RAG Service",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "rag_service.api:app",
                "--reload",
                "--port", "8081"
            ],
            "env": {
                "QDRANT_HOST": "localhost",
                "OLLAMA_HOST": "localhost"
            }
        },
        {
            "name": "Debug Tests",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": ["-v", "-s", "tests/"]
        }
    ]
}
```

---

## API Development

### FastAPI Interactive Docs

- **Swagger UI**: http://localhost:8081/docs
- **ReDoc**: http://localhost:8081/redoc

### Test Requests

```bash
# Upload a file
curl -X POST http://localhost:8081/upload \
  -F "file=@test.pdf" \
  -F 'metadata={"asignatura":"test","tipo_documento":"apuntes","auto_index":true}'

# Search
curl -X POST http://localhost:8081/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test query", "top_k": 5}'

# Index directly
curl -X POST http://localhost:8081/index \
  -H "Content-Type: application/json" \
  -d '[{"content": "Test content", "metadata": {"asignatura": "test", "tipo_documento": "apuntes"}}]'
```

### Example Upload Script

```python
# upload_example.py
import requests

# Upload and index a document
files = {'file': open('tema1.pdf', 'rb')}
metadata = {
    "asignatura": "logica-difusa",
    "tipo_documento": "apuntes",
    "tema": "Conjuntos difusos",
    "auto_index": True
}

response = requests.post(
    "http://localhost:8081/upload",
    files=files,
    data={"metadata": json.dumps(metadata)}
)

print(response.json())
```

---

## Docker Development

### Build Image

```bash
# Build with dev dependencies
docker build -f rag_service/Dockerfile \
  --build-arg INSTALL_DEV=true \
  -t rag-service:dev .
```

### Run Container

```bash
docker run -it --rm \
  -p 8081:8081 \
  -e QDRANT_HOST=host.docker.internal \
  -e OLLAMA_HOST=host.docker.internal \
  -v $(pwd)/documents:/app/documents \
  rag-service:dev
```

### Docker Compose Development

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f rag_service

# Restart after code changes
docker compose restart rag_service

# Rebuild and restart
docker compose up -d --build rag_service
```

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| `Connection refused` to Qdrant | Ensure Qdrant is running: `docker compose up -d qdrant` |
| `Connection refused` to Ollama | Ensure Ollama is running: `docker compose up -d ollama` |
| `Model not found` | Pull model: `docker exec ollama ollama pull nomic-embed-text` |
| `Dimension mismatch` | Delete collection, ensure `EMBEDDING_DIMENSION` matches model |
| `File not found` | Check `DOCUMENTS_PATH` configuration |

### Check Service Status

```bash
# Qdrant
curl http://localhost:6333/healthz

# Ollama models
curl http://localhost:11434/api/tags

# RAG Service
curl http://localhost:8081/health
```

### Reset Vector Store

```python
from rag_service.embeddings.store import get_vector_store

store = get_vector_store()
store.delete_collection()
# Collection will be recreated on next index
```

---

## Related Documentation

- [Architecture](architecture.md) - System design
- [Configuration](configuration.md) - Environment variables
- [API Endpoints](api-endpoints.md) - API reference
- [Deployment](deployment.md) - Production setup
