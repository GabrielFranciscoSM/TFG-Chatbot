import importlib
from unittest.mock import MagicMock

emb_module = importlib.import_module("rag_service.embeddings.embeddings")


def test_embed_query_and_documents(monkeypatch):
    # Mock OllamaEmbeddings class used inside EmbeddingService
    mock_emb = MagicMock()
    mock_emb.embed_query.return_value = [0.1, 0.2, 0.3]
    mock_emb.embed_documents.return_value = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]

    monkeypatch.setattr(
        emb_module, "OllamaEmbeddings", lambda base_url, model: mock_emb
    )

    svc = emb_module.EmbeddingService()
    q = svc.embed_query("hello world")
    assert isinstance(q, list) and len(q) == 3

    docs = svc.embed_documents(["a", "b"])
    assert isinstance(docs, list) and len(docs) == 2


def test_get_embedding_service_singleton(monkeypatch):
    # Ensure singleton can be created and reused
    monkeypatch.setattr(
        emb_module, "OllamaEmbeddings", lambda base_url, model: MagicMock()
    )
    emb1 = emb_module.get_embedding_service()
    emb2 = emb_module.get_embedding_service()
    assert emb1 is emb2
