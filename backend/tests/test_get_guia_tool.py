import json
import pytest

import importlib

# Import the tools module using importlib to avoid name collisions with
# `backend.logic.tools` attribute exported in `backend.logic.__init__`.
tools = importlib.import_module('backend.logic.tools.tools')


def test_get_guia_with_key_returns_value(monkeypatch, dummy_mongo_client_class):
    doc = {
        "asignatura": "TFG Test",
        "prerrequisitos_o_recomendaciones": ["Req1", "Req2"],
        "breve_descripción_de_contenidos": ["Short desc"]
    }
    # Replace MongoDBClient with a dummy that returns our document
    monkeypatch.setattr(tools, "MongoDBClient", lambda: dummy_mongo_client_class(doc=doc))

    result = tools.get_guia.invoke({"asignatura_state": "TFG Test", "key": "prerrequisitos_o_recomendaciones"})

    parsed = json.loads(result)
    assert isinstance(parsed, list)
    assert "Req1" in parsed


def test_get_guia_returns_summary_when_no_key(monkeypatch, dummy_mongo_client_class):
    doc = {
        "asignatura": "TFG Test",
        "grado": "Grado X",
        "curso": "2",
        "créditos": "6",
        "url": "http://example.com/guia",
        "breve_descripción_de_contenidos": ["One", "Two", "Three", "Four"]
    }
    monkeypatch.setattr(tools, "MongoDBClient", lambda: dummy_mongo_client_class(doc=doc))

    result = tools.get_guia.invoke({"asignatura_state": "TFG Test"})
    parsed = json.loads(result)

    assert isinstance(parsed, dict)
    assert parsed.get("asignatura") == "TFG Test"
    assert parsed.get("grado") == "Grado X"
    # brief_description should be present and be a list (trimmed to 3 items)
    assert isinstance(parsed.get("brief_description"), list)
    assert len(parsed.get("brief_description")) <= 3


def test_get_guia_no_subject_returns_no_guia_message(monkeypatch, dummy_mongo_client_class):
    # When no document exists, the tool should return a helpful message
    monkeypatch.setattr(tools, "MongoDBClient", lambda: dummy_mongo_client_class(doc=None))

    result = tools.get_guia.invoke({})
    assert isinstance(result, str)
    assert "No guia found for subject" in result


def test_get_guia_key_not_present_returns_message(monkeypatch, dummy_mongo_client_class):
    # Document exists but requested key is missing
    doc = {"asignatura": "TFG Test", "alguna_clave": "valor"}
    monkeypatch.setattr(tools, "MongoDBClient", lambda: dummy_mongo_client_class(doc=doc))

    result = tools.get_guia.invoke({"asignatura_state": "TFG Test", "key": "enlaces_recomendados"})
    assert isinstance(result, str)
    assert "not present in guia" in result
