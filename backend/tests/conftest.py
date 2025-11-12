import os
import sys
import pytest
import uuid
from langchain_core.messages import AIMessage
from backend.logic.graph import GraphAgent
from fastapi.testclient import TestClient
from backend.api import app
from backend.logic.testGraph import create_test_subgraph

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
def graph(monkeypatch):
    """Fixture que proporciona una instancia del grafo compilado.

    To avoid network calls to vLLM / Gemini during tests, we patch
    GraphAgent._get_llm to return a lightweight dummy LLM that implements
    `bind_tools` and `invoke` returning an `AIMessage`-like object.
    """
    class DummyBoundLLM:
        def bind_tools(self, tools):
            # Return self as the bound runnable; tests only call .invoke()
            return self

        def invoke(self, messages):
            # Return an AIMessage-like object expected by the graph logic
            return AIMessage(content="Test response from dummy LLM")

    monkeypatch.setattr(GraphAgent, "_get_llm", lambda self, temp=None: DummyBoundLLM())

    agent = GraphAgent()
    return agent.build_graph()

@pytest.fixture
def testGraph(monkeypatch):
    """Fixture que proporciona una instancia del grafo de test.

    Patch TestSessionGraph._get_llm to avoid external calls during subgraph
    construction (which instantiates an LLM in __init__). The dummy provides
    bind_tools and invoke so the subgraph can be constructed and invoked in tests.
    """
    import backend.logic.testGraph as tg

    class DummyBoundLLM:
        def bind_tools(self, tools):
            return self

        def invoke(self, messages):
            return AIMessage(content="Test response from dummy TestSession LLM")

    monkeypatch.setattr(tg.TestSessionGraph, "_get_llm", lambda self, temp=None: DummyBoundLLM())

    test_subgraph = create_test_subgraph()
    return test_subgraph

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


# --- Additional test doubles / factories for testGraph ---
from types import SimpleNamespace
import importlib


@pytest.fixture
def dummy_message_factory():
    """Factory to create lightweight message-like objects (content, tool_calls)."""
    def factory(content=None, tool_calls=None):
        return SimpleNamespace(content=content, tool_calls=tool_calls or [])
    return factory


@pytest.fixture
def dummy_multiple_choice_test():
    """Factory returning a minimal MultipleChoice-like object for tests.

    Usage: MCQ = dummy_multiple_choice_test; q = MCQ("Q?", ["A","B"])  # first marked correct
    """
    # Use the real Pydantic models so isinstance checks in the code under test
    # (which compare against backend.logic.models.MultipleChoiceTest) succeed.
    from backend.logic.models import MultipleChoiceTest, Question, Answer

    def factory(question_text, options):
        # options can be list of texts (first correct) or list of (text, is_correct)
        opts = []
        if options and isinstance(options[0], tuple):
            for t, is_correct in options:
                opts.append(Answer(answer_text=t, is_correct=is_correct))
        else:
            for i, t in enumerate(options):
                opts.append(Answer(answer_text=t, is_correct=(i == 0)))

        q = Question(question_text=question_text)
        return MultipleChoiceTest(question=q, options=opts)

    return factory


@pytest.fixture
def dummy_tool_factory():
    """Factory for simple tool-like objects with a name and invoke(args)."""
    def factory(name, result):
        class Tool:
            def __init__(self, name, result):
                self.name = name
                self._result = result

            def invoke(self, args):
                return self._result

        return Tool(name, result)

    return factory


@pytest.fixture
def dummy_llm_factory():
    """Factory that returns a lightweight LLM-like object with configurable reply."""
    def factory(reply_content="CORRECT: YES\nFEEDBACK: OK"):
        class DummyLLM:
            def __init__(self, reply_content):
                self.reply_content = reply_content

            def invoke(self, prompt_or_messages):
                return SimpleNamespace(content=self.reply_content)

        return DummyLLM(reply_content)

    return factory


@pytest.fixture
def patch_get_tools(monkeypatch):
    """Helper to monkeypatch backend.logic.tools.tools.get_tools to return a list of tools."""
    def _patch(tools_list):
        tools_mod = importlib.import_module("backend.logic.tools.tools")
        monkeypatch.setattr(tools_mod, "get_tools", lambda: tools_list)
        return tools_list

    return _patch


@pytest.fixture
def interrupt_simulator(monkeypatch):
    """Helper to patch the interrupt symbol in backend.logic.testGraph to return a given value."""
    import backend.logic.testGraph as tg

    def _patch(value):
        monkeypatch.setattr(tg, "interrupt", lambda payload: value)
        return value

    return _patch