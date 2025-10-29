import pytest
import json
import importlib

# Import the tools module using importlib to avoid name collisions with
# `backend.logic.tools` attribute exported in `backend.logic.__init__`.
tools = importlib.import_module('backend.logic.tools.tools')

def test_calculator_simple_expressions():
    assert tools.calculator.invoke("2 + 2") == "4"
    assert tools.calculator.invoke("5 * 3") == "15"
    assert tools.calculator.invoke("10 / 2") == "5.0"

def test_calculator_allowed_functions():
    assert tools.calculator.invoke("abs(-5)") == "5"
    assert tools.calculator.invoke("round(3.1415, 2)") == "3.14"
    assert tools.calculator.invoke("min(1, 2, 3)") == "1"
    assert tools.calculator.invoke("max(1, 2, 3)") == "3"
    assert tools.calculator.invoke("sum([1,2,3])") == "6"
    assert tools.calculator.invoke("pow(2, 3)") == "8"
    assert tools.calculator.invoke("len([1,2,3])") == "3"

def test_calculator_invalid_expression():
    result = tools.calculator.invoke("unknown_func(2)")
    assert result.startswith("Error evaluating expression:")

def test_calculator_disallowed_builtins():
    # Should not allow access to __import__ or other builtins
    result = tools.calculator.invoke("__import__('os').system('echo hello')")
    assert result.startswith("Error evaluating expression:")

def test_web_search_returns_result(monkeypatch):
    class DummySearch:
        def run(self, query):
            return f"Results for {query}"
    monkeypatch.setattr(tools, "DuckDuckGoSearchAPIWrapper", lambda: DummySearch())
    assert tools.web_search.invoke("python") == "Results for python"

def test_web_search_handles_exception(monkeypatch):
    class DummySearch:
        def run(self, query):
            raise Exception("API error")
    monkeypatch.setattr(tools, "DuckDuckGoSearchAPIWrapper", lambda: DummySearch())
    result = tools.web_search.invoke("python")
    assert result.startswith("Error performing web search:")

def test_get_tools_returns_expected_tools():
    tool_list = tools.get_tools()
    assert isinstance(tool_list, list)
    assert tools.web_search in tool_list
    assert tools.calculator in tool_list
    # Ensure get_guia tool is also registered
    assert tools.get_guia in tool_list


def test_get_guia_with_key_returns_value(monkeypatch, dummy_mongo_client_class):
    doc = {
        "asignatura": "TFG Test",
        "prerrequisitos_o_recomendaciones": ["Req1", "Req2"]
    }
    monkeypatch.setattr(tools, "MongoDBClient", lambda: dummy_mongo_client_class(doc=doc))

    # Request a specific key; pydantic should accept the key value string
    result = tools.get_guia.invoke({"asignatura_state": "TFG Test", "key": "prerrequisitos_o_recomendaciones"})

    # Should be a JSON string representing the list
    parsed = json.loads(result)
    assert isinstance(parsed, list)
    assert "Req1" in parsed


def test_get_guia_no_subject_returns_message(monkeypatch, dummy_mongo_client_class):
    # Ensure that when no subject is provided and injected state is absent,
    # the tool returns a clear error message.
    monkeypatch.setattr(tools, "MongoDBClient", lambda: dummy_mongo_client_class(doc=None))

    result = tools.get_guia.invoke({})
    assert isinstance(result, str)
    assert "No asignatura provided" in result