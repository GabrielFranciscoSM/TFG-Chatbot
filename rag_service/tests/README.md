# RAG Service Tests

This directory contains comprehensive tests for the RAG service, including both unit and integration tests.

## Test Structure

```
tests/
├── conftest.py                      # Common test fixtures and configuration
├── test_general_routes.py           # Unit tests for general endpoints (/, /health)
├── test_search_index_routes.py      # Unit tests for search and indexing endpoints
├── test_files_routes.py             # Unit tests for file management endpoints
├── test_subjects_routes.py          # Unit tests for subject listing endpoints
├── test_embeddings_service.py       # Unit tests for embedding generation
├── test_vector_store.py             # Unit tests for vector store operations
├── test_file_loader.py              # Unit tests for file loading
├── test_file_utils.py               # Unit tests for file utilities
├── test_document_processor.py       # Unit tests for document chunking
└── test_integration.py              # Integration tests for full API workflows
```

## Running Tests

### Run All Tests

```bash
# From the rag_service directory
pytest

# Or from project root
pytest rag_service/tests/
```

### Run Only Unit Tests

```bash
pytest -m unit
```

### Run Only Integration Tests

```bash
pytest -m integration
```

### Run Specific Test File

```bash
pytest tests/test_general_routes.py
```

### Run with Coverage

```bash
pytest --cov=rag_service --cov-report=html
```

### Run with Verbose Output

```bash
pytest -v
```

## Test Categories

### Unit Tests

Unit tests verify individual components in isolation using mocks and stubs. They do not require external services.

**Run unit tests:**
```bash
pytest -m unit
```

### Integration Tests

Integration tests verify the full API workflow with real services (Qdrant, Ollama). These require:
- Docker containers running (`docker-compose up -d`)
- RAG service running on port 8081
- Qdrant running on port 6333
- Ollama running on port 11434

**Run integration tests:**
```bash
# Start services first
docker-compose up -d

# Run tests
pytest -m integration
```

## Environment Variables

Integration tests can be configured with environment variables:

- `RAG_API_BASE_URL`: Base URL for RAG API (default: `http://localhost:8081`)
- `API_TIMEOUT`: Timeout for API requests in seconds (default: `30`)

Example:
```bash
RAG_API_BASE_URL=http://localhost:8081 pytest -m integration
```

## Test Coverage

The tests cover:

### Routes (API Endpoints)
- ✅ General routes (`/`, `/health`)
- ✅ Search and indexing (`/search`, `/index`, `/collection/info`)
- ✅ File management (`/files`, `/load-file`, `/upload`)
- ✅ Subject management (`/subjects`, `/subjects/{asignatura}/types`)

### Services
- ✅ Embedding service (query and document embeddings)
- ✅ Vector store (indexing, searching, collection management)
- ✅ Document processor (chunking, metadata preservation)
- ✅ File loader (loading different file formats)
- ✅ File utilities (listing files, subjects, document types)

### Integration Workflows
- ✅ Index and search workflow
- ✅ Search with filters
- ✅ Similarity threshold filtering
- ✅ Health checks and service availability
- ✅ Error handling and validation

## Writing New Tests

### Unit Test Template

```python
"""Unit tests for <module_name>."""

import pytest
import importlib

module = importlib.import_module("rag_service.<module_path>")


def test_feature_name(api_client, monkeypatch):
    """Test description."""
    # Arrange
    # ... setup mocks and test data
    
    # Act
    # ... perform action
    
    # Assert
    # ... verify results
```

### Integration Test Template

```python
@pytest.mark.integration
def test_feature_integration(rag_api_base_url, api_timeout):
    """Test description."""
    # Arrange
    payload = {...}
    
    # Act
    response = requests.post(
        f"{rag_api_base_url}/endpoint",
        json=payload,
        timeout=api_timeout
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "expected_field" in data
```

## Continuous Integration

Tests are designed to run in CI/CD pipelines:

1. Unit tests run on every commit (no external dependencies)
2. Integration tests run when services are available
3. Use markers to selectively run test suites

Example CI configuration:
```yaml
# Run unit tests
pytest -m unit

# Run integration tests (with services)
docker-compose up -d
pytest -m integration
docker-compose down
```

## Troubleshooting

### Integration Tests Failing

1. **Check services are running:**
   ```bash
   docker-compose ps
   ```

2. **Check service health:**
   ```bash
   curl http://localhost:8081/health
   ```

3. **View service logs:**
   ```bash
   docker-compose logs rag_service
   docker-compose logs qdrant
   docker-compose logs ollama
   ```

### Mock Issues in Unit Tests

If mocks aren't working:
1. Verify import paths are correct
2. Check that you're patching the right module
3. Use `importlib.import_module()` to avoid import name conflicts

### Fixture Not Found

Ensure `conftest.py` is in the right location and pytest can discover it:
```bash
pytest --fixtures
```
