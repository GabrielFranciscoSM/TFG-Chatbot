import importlib

import requests

tools = importlib.import_module("backend.logic.tools.tools")


def test_rag_search_success(monkeypatch):
    class DummyResp:
        def __init__(self, data):
            self._data = data

        def raise_for_status(self):
            return None

        def json(self):
            return self._data

    def fake_post(url, json=None, timeout=None):
        assert url.endswith("/search")
        return DummyResp(
            {
                "results": [{"content": "snippet", "score": 0.95}],
                "total_results": 1,
                "query": json.get("query"),
            }
        )

    monkeypatch.setattr(tools.requests, "post", fake_post)

    result = tools.rag_search.invoke(
        {"query": "prueba", "asignatura": "TFG Test", "top_k": 1}
    )
    # New structured return is a dict
    assert isinstance(result, dict)
    assert result.get("ok") is True
    assert result.get("total_results") == 1
    assert "results" in result
    assert result["results"][0]["content"] == "snippet"


def test_rag_search_handles_request_exception(monkeypatch):
    def raise_exc(url, json=None, timeout=None):
        raise requests.exceptions.RequestException("connect error")

    monkeypatch.setattr(tools.requests, "post", raise_exc)

    result = tools.rag_search.invoke({"query": "prueba"})
    assert isinstance(result, dict)
    assert result.get("ok") is False
    assert "Error contacting RAG service" in result.get("error", "")
