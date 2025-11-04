import os
import sys
import pytest
import uuid
from langchain_core.messages import AIMessage
from backend.logic.graph import GraphAgent
from fastapi.testclient import TestClient
from backend.api import app

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
def api_client():
    """Fixture que proporciona un cliente de pruebas para la API de FastAPI."""
    return TestClient(app)

@pytest.fixture
def session_id():
    """Fixture que proporciona un ID de sesión único para cada test."""
    return f"test-session-{uuid.uuid4()}"


@pytest.fixture
def dummy_mongo_client_class():
    """Provide a DummyMongoClient class for tests to monkeypatch MongoDBClient."""
    class DummyMongoClient:
        def __init__(self, doc=None):
            self._doc = doc

        def connect(self):
            return None

        def close(self):
            return None

        def find_by_subject(self, collection, subject):
            if not self._doc:
                return None
            if subject == self._doc.get("asignatura"):
                return self._doc
            return None

    return DummyMongoClient