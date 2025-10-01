import os
import sys
import pytest
from unittest.mock import Mock, patch
from langchain_core.messages import AIMessage

# Get the absolute path of the project root
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

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
def mock_chat_openai():
    with patch('backend.logic.graph.ChatOpenAI') as mock:
        # Configure the mock to return a predictable response
        mock_instance = Mock()
        mock_instance.invoke.return_value = AIMessage(content="Test response")
        mock.return_value = mock_instance
        yield mock