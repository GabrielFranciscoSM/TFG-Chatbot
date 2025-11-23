import os
import sys
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

# Ensure project root is importable
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT_DIR)

from rag_service import config  # noqa: E402
from rag_service.api import app  # noqa: E402


@pytest.fixture(autouse=True)
def mock_external_services(monkeypatch):
    """Mock external services (Qdrant, Ollama) to prevent connection errors during tests."""
    # Mock QdrantClient
    mock_qdrant = MagicMock()
    mock_qdrant.get_collections.return_value = MagicMock(collections=[])

    # Mock QdrantClient constructor in store module
    monkeypatch.setattr(
        "rag_service.embeddings.store.QdrantClient", lambda host, port: mock_qdrant
    )

    # Mock EmbeddingService
    mock_embedding_service = MagicMock()
    mock_embedding_service.embed_query.return_value = [0.1] * 768
    mock_embedding_service.embed_documents.return_value = [[0.1] * 768]

    # Mock get_embedding_service to return the mock
    monkeypatch.setattr(
        "rag_service.embeddings.store.get_embedding_service",
        lambda: mock_embedding_service,
    )
    monkeypatch.setattr(
        "rag_service.embeddings.embeddings.get_embedding_service",
        lambda: mock_embedding_service,
    )

    # Mock OllamaEmbeddings to avoid connection attempts
    monkeypatch.setattr(
        "rag_service.embeddings.embeddings.OllamaEmbeddings", MagicMock()
    )


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset all singleton instances before each test."""
    # Reset vector store singleton
    try:
        from rag_service.embeddings import store

        store._vector_store = None
    except Exception:
        pass

    # Reset embedding service singleton
    try:
        from rag_service.embeddings import embeddings

        embeddings._embedding_service = None
    except Exception:
        pass

    # Reset document processor singleton
    try:
        from rag_service.documents import document_processor

        document_processor._document_processor = None
    except Exception:
        pass

    # Reset file loader singleton
    try:
        from rag_service.documents import file_loader

        file_loader._file_loader = None
    except Exception:
        pass

    yield


@pytest.fixture
def tmp_documents_dir(tmp_path, monkeypatch):
    """Fixture that points the service to a temporary documents directory and
    updates modules that cached the path at import time.
    """
    # Point settings to tmp path
    monkeypatch.setenv("DOCUMENTS_PATH", str(tmp_path))
    config.settings.documents_path = str(tmp_path)

    # Update file_utils.documents_path which is evaluated at import time
    try:
        from rag_service.documents import file_utils

        file_utils.documents_path = tmp_path
    except Exception:
        # best-effort; tests will still use tmp_path directly when needed
        pass

    return tmp_path


@pytest.fixture
def api_client(tmp_documents_dir):
    """Test client that ensures the service uses the temporary documents dir."""
    return TestClient(app)
