import os
import sys
import pytest
import uuid
from langchain_core.messages import AIMessage

# Get the absolute path of the project root
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))

# Add the root directory to the Python path
sys.path.insert(0, ROOT_DIR)

@pytest.fixture(scope="session")
def root_path():
    """Fixture to provide the root path of the project."""
    return ROOT_DIR

@pytest.fixture
def mock_llm_response():
    """Create a proper AIMessage for mocking."""
    return AIMessage(content="Test response")

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

@pytest.fixture
def graph():
    """Fixture que proporciona una instancia del grafo compilado."""
    agent = GraphAgent()
    return agent.build_graph()

@pytest.fixture
def graph_config():
    """Fixture que proporciona la configuración necesaria para el checkpointer."""
    return {"configurable": {"thread_id": f"test-{uuid.uuid4()}"}}

@pytest.fixture(scope="session")
def api_base_url():
    """Fixture que proporciona la URL base de la API."""
    # Se puede configurar mediante variable de entorno
    return os.getenv("API_BASE_URL", "http://localhost:8080")

@pytest.fixture
def session_id():
    """Fixture que proporciona un ID de sesión único para cada test."""
    return f"test-session-{uuid.uuid4()}"