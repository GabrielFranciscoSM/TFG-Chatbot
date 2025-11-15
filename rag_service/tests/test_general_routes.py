"""Unit tests for general routes (root and health check)."""

from unittest.mock import MagicMock

import pytest


def test_root_endpoint(api_client):
    """Test that root endpoint returns API information."""
    resp = api_client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert "name" in data
    assert data["name"] == "RAG Service"
    assert "status" in data
    assert data["status"] == "running"
    assert "description" in data
    assert "version" in data


@pytest.mark.integration
def test_health_check_healthy(api_client, monkeypatch):
    """Test health check when Qdrant is connected."""
    from rag_service.embeddings import store

    mock_store = MagicMock()
    mock_store.get_collection_info.return_value = {
        "name": "academic_documents",
        "vectors_count": 0,
        "points_count": 10,
        "status": "green",
    }

    monkeypatch.setattr(store, "get_vector_store", lambda: mock_store)

    resp = api_client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["qdrant_connected"] is True
    assert data["collection"] is not None
    assert data["collection"]["name"] == "academic_documents"
    assert "message" in data


def test_health_check_unhealthy(api_client, monkeypatch):
    """Test health check when Qdrant connection fails."""
    import sys

    general_module = sys.modules["rag_service.routes.general"]

    def raise_error():
        raise ConnectionError("Cannot connect to Qdrant")

    # Patch at the point of use in the general module
    monkeypatch.setattr(general_module, "get_vector_store", raise_error)

    resp = api_client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "unhealthy"
    assert data["qdrant_connected"] is False
    assert data["collection"] is None
    assert "message" in data
    assert "Cannot connect to Qdrant" in data["message"]
