import os
import sys
import pytest
from langchain_core.messages import AIMessage
from backend.logic.graph import build_graph
import uuid

# Get the absolute path of the project root
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))

# Add the root directory to the Python path
sys.path.insert(0, ROOT_DIR)

@pytest.fixture(scope="session")
def root_path():
    """Fixture to provide the root path of the project."""
    return ROOT_DIR

@pytest.fixture(scope="session")
def backend_path():
    """Fixture to provide the backend directory path."""
    return os.path.join(ROOT_DIR, "backend")

@pytest.fixture
def mock_llm_response():
    """Create a proper AIMessage for mocking."""
    return AIMessage(content="Test response")
import uuid

@pytest.fixture
def graph():
    """Fixture que proporciona una instancia del grafo compilado."""
    return build_graph()

@pytest.fixture
def graph_config():
    """Fixture que proporciona la configuración necesaria para el checkpointer."""
    return {"configurable": {"thread_id": f"test-{uuid.uuid4()}"}}
@pytest.fixture
def mock_llm_with_tools():
    """Create an AIMessage with tool calls."""
    return AIMessage(
        content="",
        tool_calls=[
            {
                "name": "web_search",
                "args": {"query": "test query"},
                "id": "call_123"
            }
        ]
    )