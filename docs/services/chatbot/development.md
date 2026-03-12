# Chatbot Development Guide

This guide covers local development setup, testing, and debugging for the Chatbot Service.

## Prerequisites

- **Python 3.12+**
- **uv** (recommended) or pip
- **MongoDB** (local or Docker)
- **LLM API Key** (Gemini recommended for development)

## Quick Start

### 1. Clone and Install

```bash
# Clone repository
git clone https://github.com/your-repo/TFG-Chatbot.git
cd TFG-Chatbot

# Create virtual environment with uv
uv venv
source .venv/bin/activate  # Linux/Mac
# or: .venv\Scripts\activate  # Windows

# Install chatbot with dev dependencies
uv pip install -e "./chatbot[dev]"
```

### 2. Configure Environment

Create `.env` file in project root:

```bash
# LLM Provider (easiest for development)
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-api-key-here
GEMINI_MODEL=gemini-2.5-flash

# Service URLs (for local development)
RAG_SERVICE_URL=http://localhost:8081
BACKEND_SERVICE_URL=http://localhost:8000

# MongoDB (local instance)
MONGO_HOSTNAME=localhost
MONGO_PORT=27017
DB_NAME=tfg_chatbot

# Disable observability for faster startup
PHOENIX_ENABLED=false
```

### 3. Start Dependencies

```bash
# Start MongoDB with Docker
docker run -d --name mongodb -p 27017:27017 mongo:7

# Or start full stack
docker compose up -d mongodb rag_service
```

### 4. Run the Service

```bash
# Development mode with auto-reload
uvicorn chatbot.api:app --host 0.0.0.0 --port 8080 --reload

# Or using Python module
python -m chatbot
```

### 5. Verify

```bash
# Health check
curl http://localhost:8080/health

# System info
curl http://localhost:8080/system/info
```

---

## Project Structure

```
chatbot/
├── __init__.py           # Package init with version
├── __main__.py           # CLI entry point
├── api.py                # FastAPI application
├── config.py             # Pydantic settings
├── models.py             # API models
├── events.py             # Event logging
├── instrumentation.py    # Phoenix setup
├── logging_config.py     # Structured logging
│
├── db/
│   └── mongo.py          # MongoDB client
│
├── logic/
│   ├── graph.py          # Main GraphAgent
│   ├── testGraph.py      # Test session subgraph
│   ├── prompts.py        # System prompts
│   ├── difficulty.py     # Difficulty classifier
│   ├── profile_manager.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── tool_models.py
│   │   └── student_profile.py
│   │
│   └── tools/
│       ├── tools.py      # Tool registry
│       ├── rag.py
│       ├── guia.py
│       └── test_gen.py
│
├── storage/              # Generated at runtime
│   └── checkpoints.db    # LangGraph state
│
└── tests/
    ├── conftest.py       # Pytest fixtures
    ├── test_graph.py
    ├── test_difficulty.py
    └── ...
```

---

## Testing

### Run All Tests

```bash
# Run all chatbot tests
pytest chatbot/tests/ -v

# With coverage
pytest chatbot/tests/ --cov=chatbot --cov-report=html

# Only unit tests
pytest chatbot/tests/ -m unit -v
```

### Test Categories

Tests are organized with pytest markers:

```python
@pytest.mark.unit
def test_difficulty_classification():
    """Fast unit test, no external deps."""
    pass

@pytest.mark.integration
def test_rag_tool_real():
    """Requires RAG service running."""
    pass
```

### Key Test Files

| File | Coverage |
|------|----------|
| `test_graph.py` | GraphAgent, state management |
| `test_testGraph.py` | Test session subgraph |
| `test_difficulty.py` | Difficulty classifier |
| `test_tools.py` | Tool implementations |
| `test_prompts.py` | Prompt templates |
| `test_profile_manager.py` | Student profiles |

### Fixtures

Common fixtures in `conftest.py`:

```python
@pytest.fixture
def mock_llm():
    """Mock LLM for testing without API calls."""
    with patch("chatbot.logic.graph.ChatGoogleGenerativeAI") as mock:
        mock.return_value.invoke.return_value = AIMessage(content="Test response")
        yield mock

@pytest.fixture
def mock_mongo():
    """Mock MongoDB client."""
    with patch("chatbot.db.mongo.MongoClient") as mock:
        yield mock

@pytest.fixture
def graph_agent(mock_llm):
    """GraphAgent with mocked LLM."""
    return GraphAgent(llm_provider="gemini")
```

### Testing Tools

```python
def test_rag_search_success(mocker):
    """Test RAG search tool."""
    mocker.patch("requests.post").return_value.json.return_value = {
        "results": [{"content": "Docker info", "score": 0.9}]
    }
    
    result = rag_search.func(query="Docker", asignatura="iv")
    
    assert result["ok"] is True
    assert len(result["results"]) > 0

def test_rag_search_timeout(mocker):
    """Test timeout handling."""
    mocker.patch("requests.post").side_effect = requests.exceptions.Timeout()
    
    result = rag_search.func(query="test")
    
    assert result["ok"] is False
    assert "timeout" in result["error"].lower()
```

### Testing Graph Flow

```python
def test_chat_flow(graph_agent, mock_llm):
    """Test complete chat flow."""
    response = graph_agent.call_agent(
        query="¿Qué es Docker?",
        id="test-session",
        asignatura="iv"
    )
    
    assert "messages" in response
    assert len(response["messages"]) > 0
```

---

## Debugging

### Logging Configuration

The service uses structured JSON logging:

```python
# chatbot/logging_config.py
import logging
from pythonjsonlogger import jsonlogger

def setup_logging():
    handler = logging.StreamHandler()
    handler.setFormatter(jsonlogger.JsonFormatter())
    logging.root.addHandler(handler)
    logging.root.setLevel(logging.DEBUG)
```

Set log level via environment:

```bash
LOG_LEVEL=DEBUG uvicorn chatbot.api:app --reload
```

### Debug LangGraph

Enable LangGraph debugging:

```python
import logging
logging.getLogger("langgraph").setLevel(logging.DEBUG)
```

### Inspect Checkpoints

View saved conversation state:

```python
import sqlite3

conn = sqlite3.connect("chatbot/storage/checkpoints.db")
cursor = conn.cursor()

# List all threads
cursor.execute("SELECT DISTINCT thread_id FROM checkpoints")
threads = cursor.fetchall()

# Get state for a thread
cursor.execute(
    "SELECT * FROM checkpoints WHERE thread_id = ? ORDER BY created_at DESC LIMIT 1",
    ("session-123",)
)
```

### API Debugging

Use FastAPI's interactive docs:

```
http://localhost:8080/docs
```

Or test with curl:

```bash
# Chat request
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Qué es Docker?",
    "id": "test-session",
    "asignatura": "iv"
  }'

# Resume test session
curl -X POST http://localhost:8080/resume_chat \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-session",
    "user_response": "Un contenedor es..."
  }'
```

---

## Development Workflows

### Adding a New Tool

1. **Create tool file**:

```python
# chatbot/logic/tools/my_tool.py
from langchain.tools import tool
from pydantic import BaseModel, Field

class MyToolInput(BaseModel):
    query: str = Field(..., description="Query")

@tool(args_schema=MyToolInput)
def my_tool(query: str) -> str:
    """Description for LLM."""
    return f"Result for {query}"
```

2. **Register in tools.py**:

```python
from chatbot.logic.tools.my_tool import my_tool

AVAILABLE_TOOLS = [
    get_guia,
    rag_search,
    generate_test,
    my_tool,
]
```

3. **Add graph node** (in `graph.py`):

```python
def my_tool_node(self, state):
    # Implementation
    pass

def build_graph(self):
    graph_builder.add_node("my_tool", self.my_tool_node)
    graph_builder.add_conditional_edges(
        "agent", self.should_continue,
        {"my_tool": "my_tool", ...}
    )
    graph_builder.add_edge("my_tool", "agent")
```

4. **Write tests**:

```python
def test_my_tool():
    result = my_tool.func(query="test")
    assert "test" in result
```

### Modifying Prompts

Prompts are in `chatbot/logic/prompts.py`:

```python
# Difficulty-based prompts
SYSTEM_PROMPT_BASIC = """..."""
SYSTEM_PROMPT_INTERMEDIATE = """..."""
SYSTEM_PROMPT_ADVANCED = """..."""

# Test prompts
TEST_GENERATION_PROMPT = """..."""
TEST_EVALUATION_PROMPT = """..."""
```

Test prompt changes:

```bash
pytest chatbot/tests/test_prompts.py -v
```

### Changing LLM Providers

Switch providers for testing:

```bash
# Use Gemini
LLM_PROVIDER=gemini GEMINI_API_KEY=... python -m chatbot

# Use Mistral
LLM_PROVIDER=mistral MISTRAL_API_KEY=... python -m chatbot

# Use vLLM (requires vLLM server)
LLM_PROVIDER=vllm VLLM_HOST=localhost python -m chatbot
```

---

## Code Style

### Formatting

```bash
# Format code
black chatbot/
isort chatbot/

# Lint
ruff check chatbot/
```

### Type Checking

```bash
# Run mypy
mypy chatbot/
```

### Pre-commit Hooks

```bash
# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

---

## Common Issues

### LLM API Errors

**Problem**: `GEMINI_API_KEY not found`

**Solution**:
```bash
export GEMINI_API_KEY=your-key
# Or add to .env file
```

### MongoDB Connection Failed

**Problem**: `Cannot connect to MongoDB`

**Solution**:
```bash
# Check MongoDB is running
docker ps | grep mongo

# Start if needed
docker run -d --name mongodb -p 27017:27017 mongo:7
```

### Checkpoint Database Locked

**Problem**: `database is locked`

**Solution**:
```bash
# Stop all instances
pkill -f "uvicorn chatbot"

# Remove stale lock (if needed)
rm chatbot/storage/checkpoints.db-journal
```

### RAG Service Timeout

**Problem**: `RAG service timeout`

**Solution**:
1. Check RAG service is running: `curl http://localhost:8081/health`
2. Increase timeout in code
3. Use mock for development

---

## IDE Setup

### VS Code

Recommended extensions:
- Python
- Pylance
- Python Debugger
- Black Formatter

`.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
    "python.analysis.typeCheckingMode": "basic",
    "editor.formatOnSave": true,
    "[python]": {
        "editor.defaultFormatter": "ms-python.black-formatter"
    }
}
```

### Launch Configuration

`.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Chatbot API",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "chatbot.api:app",
                "--host", "0.0.0.0",
                "--port", "8080",
                "--reload"
            ],
            "envFile": "${workspaceFolder}/.env"
        },
        {
            "name": "Pytest Current File",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": ["${file}", "-v"],
            "console": "integratedTerminal"
        }
    ]
}
```

---

## Related Documentation

- [Architecture](architecture.md) - System design
- [Configuration](configuration.md) - Environment variables
- [API Endpoints](api-endpoints.md) - API reference
- [LangGraph](langgraph.md) - Agent internals
- [Tools](tools.md) - Tool implementations
