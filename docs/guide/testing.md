---
layout: default
title: Testing Guide
parent: Developer Guide
nav_order: 4
---

# Testing Guide

Comprehensive guide to running and writing tests for the TFG-Chatbot project.

---

## Test Overview

The project has four levels of tests:

| Type | Location | Marker | Count | Requires |
|------|----------|--------|-------|----------|
| **Unit** | `*/tests/` | `@pytest.mark.unit` | ~50 | Nothing |
| **Integration** | `tests/integration/` | `@pytest.mark.integration` | 29 | Services running |
| **Infrastructure** | `tests/infrastructure/` | `@pytest.mark.container` | 69 | Containers running |
| **Math Investigation** | `math_investigation/` | - | 41 | Nothing |

---

## Running Unit Tests

Unit tests don't require any services to be running:

```bash
# All unit tests
uv run pytest backend/tests/ chatbot/tests/ rag_service/tests/ -m unit -v

# Specific service
uv run pytest backend/tests/ -m unit -v
uv run pytest chatbot/tests/ -m unit -v
uv run pytest rag_service/tests/ -m unit -v

# With coverage
uv run pytest backend/tests/ -m unit --cov=backend

# Specific test file
uv run pytest backend/tests/test_users.py -v
```

---

## Running Integration Tests

Integration tests require all services to be running:

### Prerequisites

```bash
# 1. Start services
docker compose up -d

# 2. Wait for health checks
curl http://localhost:8000/health
curl http://localhost:8081/health

# 3. Initialize Ollama (first time)
./scripts/init_ollama.sh
```

### Execute Tests

```bash
# All integration tests
uv run pytest tests/integration/ -m integration -v

# With verbose output
uv run pytest tests/integration/ -m integration -v -s

# Specific test file
uv run pytest tests/integration/test_rag_service.py -m integration

# Specific test
uv run pytest tests/integration/test_rag_service.py::test_rag_index_and_search_workflow -m integration
```

### Environment Variables

```bash
# Customize endpoints
export API_BASE_URL="http://localhost:8000"
export RAG_BASE_URL="http://localhost:8081"
export API_TIMEOUT="60"
```

---

## Running Infrastructure Tests

Infrastructure tests verify container health:

### Prerequisites

```bash
# All containers must be running
docker compose up -d
docker compose ps
```

### Execute Tests

```bash
# All infrastructure tests
uv run pytest tests/infrastructure/ -m container -v

# Specific service tests
uv run pytest tests/infrastructure/test_mongo_container.py -v
uv run pytest tests/infrastructure/test_backend_container.py -v
uv run pytest tests/infrastructure/test_ollama_container.py -v
uv run pytest tests/infrastructure/test_qdrant_container.py -v
uv run pytest tests/infrastructure/test_rag_service_container.py -v
uv run pytest tests/infrastructure/test_chatbot_container.py -v
uv run pytest tests/infrastructure/test_frontend_container.py -v

# vLLM tests (only if LLM_PROVIDER=vllm)
LLM_PROVIDER=vllm uv run pytest tests/infrastructure/test_vllm_container.py -v
```

---

## Running Math Investigation Tests

```bash
# All math tests
uv run pytest math_investigation/ -v

# Specific module
uv run pytest math_investigation/clustering/ -v
uv run pytest math_investigation/nlp/ -v
uv run pytest math_investigation/topic_modeling/ -v

# Quick summary
uv run pytest math_investigation/ --tb=short -q
```

---

## Running Tests in Containers

Use the helper script for container-based testing:

```bash
# All services
./scripts/run_tests.sh all

# Specific service
./scripts/run_tests.sh chatbot
./scripts/run_tests.sh backend
./scripts/run_tests.sh rag

# With pytest arguments
./scripts/run_tests.sh rag -k "test_embeddings"

# Skip rebuild (faster)
./scripts/run_tests.sh all --no-rebuild
```

### Test Reports

Reports are generated in `test-reports/`:

```
test-reports/
├── test-report_2024-01-31_17-59-32.md
├── test-report_2024-01-31_19-33-11.md
└── ...
```

---

## Writing New Tests

### Unit Test Example

```python
# backend/tests/test_users.py
import pytest
from backend.models import User

@pytest.mark.unit
def test_create_user(test_db):
    """Test user creation."""
    from backend.db.users import create_user
    
    user = create_user(
        test_db, 
        username="testuser", 
        password="testpass",
        role="student"
    )
    
    assert user.username == "testuser"
    assert user.role == "student"
```

### Integration Test Example

```python
# tests/integration/test_backend.py
import pytest
import requests

@pytest.mark.integration
def test_chat_endpoint(auth_headers):
    """Test chat endpoint with authentication."""
    response = requests.post(
        "http://localhost:8000/chat",
        json={"message": "Hello"},
        headers=auth_headers,
        timeout=30
    )
    
    assert response.status_code == 200
    assert "response" in response.json()
```

### Infrastructure Test Example

```python
# tests/infrastructure/test_mongo_container.py
import pytest

pytestmark = pytest.mark.container

def test_mongo_connection(mongo_client):
    """Test MongoDB is accessible."""
    server_info = mongo_client.server_info()
    assert "version" in server_info

def test_mongo_write_read(mongo_client):
    """Test basic CRUD operations."""
    db = mongo_client["test_db"]
    collection = db["test_collection"]
    
    # Insert
    result = collection.insert_one({"name": "test"})
    assert result.inserted_id
    
    # Read
    doc = collection.find_one({"name": "test"})
    assert doc["name"] == "test"
```

---

## Test Fixtures

### Backend Fixtures (`backend/tests/conftest.py`)

```python
@pytest.fixture
def test_db():
    """Provides a mock MongoDB database."""
    import mongomock
    client = mongomock.MongoClient()
    return client["test_db"]

@pytest.fixture
def test_user(test_db):
    """Creates a test user."""
    from backend.db.users import create_user
    return create_user(test_db, "testuser", "testpass", "student")
```

### Infrastructure Fixtures (`tests/infrastructure/conftest.py`)

```python
@pytest.fixture
def mongo_client():
    """Provides MongoDB client with cleanup."""
    from pymongo import MongoClient
    client = MongoClient("mongodb://root:example@localhost:27017")
    yield client
    # Cleanup test databases
    for db_name in client.list_database_names():
        if db_name.startswith("test_"):
            client.drop_database(db_name)
    client.close()
```

---

## Test Markers

Available pytest markers:

| Marker | Purpose |
|--------|---------|
| `@pytest.mark.unit` | Unit tests (no external deps) |
| `@pytest.mark.integration` | Integration tests (requires services) |
| `@pytest.mark.container` | Infrastructure tests (requires containers) |
| `@pytest.mark.slow` | Slow tests (skip with `-m "not slow"`) |

### Using Markers

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Exclude slow tests
pytest -m "not slow"

# Combine markers
pytest -m "unit and not slow"
```

---

## Coverage Reports

```bash
# Generate coverage report
uv run pytest backend/tests/ --cov=backend --cov-report=html

# View report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

---

## Continuous Integration

Tests run automatically on GitHub Actions:

- **Push to main**: All unit tests
- **Pull Request**: Unit + integration tests
- **Nightly**: Full test suite including infrastructure

See `.github/workflows/` for CI configuration.
