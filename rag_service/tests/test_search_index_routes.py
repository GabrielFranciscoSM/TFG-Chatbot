"""Unit tests for search and indexing routes."""

from unittest.mock import MagicMock


def test_search_endpoint_success(api_client, monkeypatch):
    """Test successful semantic search."""
    import sys

    search_index_module = sys.modules["rag_service.routes.search_index"]
    from rag_service.models import SearchResult

    # Mock embedding service to return proper dimensions
    mock_embeddings = MagicMock()
    mock_embeddings.embed_query.return_value = [0.1] * 768

    mock_store = MagicMock()
    mock_store.embedding_service = mock_embeddings
    mock_store.search.return_value = [
        SearchResult(
            content="This is a test document about fuzzy logic",
            metadata={"asignatura": "Lógica Difusa", "tipo_documento": "apuntes"},
            score=0.85,
        ),
        SearchResult(
            content="Another document about fuzzy sets",
            metadata={"asignatura": "Lógica Difusa", "tipo_documento": "ejercicios"},
            score=0.75,
        ),
    ]

    monkeypatch.setattr(search_index_module, "get_vector_store", lambda: mock_store)

    payload = {"query": "fuzzy logic", "asignatura": "Lógica Difusa", "top_k": 5}

    resp = api_client.post("/search", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "results" in data
    assert data["total_results"] == 2
    assert data["query"] == "fuzzy logic"
    assert len(data["results"]) == 2
    assert data["results"][0]["score"] == 0.85


def test_search_endpoint_with_filters(api_client, monkeypatch):
    """Test search with filters."""
    import sys

    search_index_module = sys.modules["rag_service.routes.search_index"]
    from rag_service.models import SearchResult

    # Mock embedding service
    mock_embeddings = MagicMock()
    mock_embeddings.embed_query.return_value = [0.1] * 768

    mock_store = MagicMock()
    mock_store.embedding_service = mock_embeddings
    mock_store.search.return_value = [
        SearchResult(
            content="Exam document",
            metadata={"asignatura": "Math", "tipo_documento": "examen"},
            score=0.9,
        )
    ]

    monkeypatch.setattr(search_index_module, "get_vector_store", lambda: mock_store)

    payload = {
        "query": "test query",
        "asignatura": "Math",
        "tipo_documento": "examen",
        "similarity_threshold": 0.7,
    }

    resp = api_client.post("/search", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_results"] == 1

    # Verify filters were passed to search
    mock_store.search.assert_called_once()
    call_args = mock_store.search.call_args
    assert call_args.kwargs["filters"] == {
        "asignatura": "Math",
        "tipo_documento": "examen",
    }


def test_search_endpoint_no_results(api_client, monkeypatch):
    """Test search returning no results."""
    import sys

    search_index_module = sys.modules["rag_service.routes.search_index"]

    # Mock embedding service
    mock_embeddings = MagicMock()
    mock_embeddings.embed_query.return_value = [0.1] * 768

    mock_store = MagicMock()
    mock_store.embedding_service = mock_embeddings
    mock_store.search.return_value = []

    monkeypatch.setattr(search_index_module, "get_vector_store", lambda: mock_store)

    payload = {"query": "nonexistent topic"}

    resp = api_client.post("/search", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_results"] == 0
    assert data["results"] == []


def test_search_endpoint_error(api_client, monkeypatch):
    """Test search endpoint handling errors."""
    from rag_service.embeddings import store

    def raise_error(*args, **kwargs):
        raise RuntimeError("Search failed")

    mock_store = MagicMock()
    mock_store.search = raise_error

    monkeypatch.setattr(store, "get_vector_store", lambda: mock_store)

    payload = {"query": "test"}

    resp = api_client.post("/search", json=payload)
    assert resp.status_code == 500
    data = resp.json()
    assert "Search failed" in data["detail"]


def test_index_documents_success(api_client, monkeypatch):
    """Test successful document indexing."""
    import sys

    search_index_module = sys.modules["rag_service.routes.search_index"]

    # Mock embedding service to return proper embeddings
    mock_embeddings = MagicMock()
    mock_embeddings.embed_documents.return_value = [[0.1] * 768, [0.2] * 768]

    mock_store = MagicMock()
    mock_store.embedding_service = mock_embeddings
    mock_store.index_documents.return_value = 3

    monkeypatch.setattr(search_index_module, "get_vector_store", lambda: mock_store)

    payload = [
        {
            "content": "Document 1",
            "metadata": {
                "asignatura": "Test",
                "tipo_documento": "apuntes",
                "fecha": "2025-11-04",
            },
        },
        {
            "content": "Document 2",
            "metadata": {
                "asignatura": "Test",
                "tipo_documento": "ejercicios",
                "fecha": "2025-11-04",
            },
        },
    ]

    resp = api_client.post("/index", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["indexed_count"] == 3
    assert "collection_name" in data
    assert "timestamp" in data


def test_index_documents_empty_list(api_client, monkeypatch):
    """Test indexing empty document list."""
    from rag_service.embeddings import store

    mock_store = MagicMock()
    mock_store.index_documents.return_value = 0

    monkeypatch.setattr(store, "get_vector_store", lambda: mock_store)

    resp = api_client.post("/index", json=[])
    assert resp.status_code == 200
    data = resp.json()
    assert data["indexed_count"] == 0


def test_index_documents_error(api_client, monkeypatch):
    """Test indexing error handling."""
    from rag_service.embeddings import store

    def raise_error(*args, **kwargs):
        raise ValueError("Invalid document format")

    mock_store = MagicMock()
    mock_store.index_documents = raise_error

    monkeypatch.setattr(store, "get_vector_store", lambda: mock_store)

    payload = [
        {
            "content": "Test",
            "metadata": {
                "asignatura": "Test",
                "tipo_documento": "apuntes",
                "fecha": "2025-11-04",
            },
        }
    ]

    resp = api_client.post("/index", json=payload)
    assert resp.status_code == 500
    data = resp.json()
    assert "Indexing failed" in data["detail"]


def test_get_collection_info_success(api_client, monkeypatch):
    """Test getting collection information."""
    import sys

    search_index_module = sys.modules["rag_service.routes.search_index"]

    # Mock embedding service (needed for store initialization)
    mock_embeddings = MagicMock()

    mock_store = MagicMock()
    mock_store.embedding_service = mock_embeddings
    mock_store.get_collection_info.return_value = {
        "name": "academic_documents",
        "vectors_count": 100,
        "points_count": 50,
        "status": "green",
    }

    monkeypatch.setattr(search_index_module, "get_vector_store", lambda: mock_store)

    resp = api_client.get("/collection/info")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "academic_documents"
    assert data["vectors_count"] == 100
    assert data["points_count"] == 50
    assert data["status"] == "green"


def test_get_collection_info_error(api_client, monkeypatch):
    """Test collection info error handling."""
    import sys

    search_index_module = sys.modules["rag_service.routes.search_index"]

    # Mock embedding service
    mock_embeddings = MagicMock()

    def raise_error():
        raise RuntimeError("Collection not found")

    mock_store = MagicMock()
    mock_store.embedding_service = mock_embeddings
    mock_store.get_collection_info = raise_error

    monkeypatch.setattr(search_index_module, "get_vector_store", lambda: mock_store)

    resp = api_client.get("/collection/info")
    assert resp.status_code == 500
    data = resp.json()
    assert "Failed to get collection info" in data["detail"]
