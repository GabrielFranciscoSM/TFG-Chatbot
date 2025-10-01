import pytest
from backend.logic import tools

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