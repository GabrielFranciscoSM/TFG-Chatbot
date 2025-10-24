from unittest.mock import MagicMock, patch
import importlib
import pytest

store_module = importlib.import_module("rag_service.embeddings.store")
emb_module = importlib.import_module("rag_service.embeddings.embeddings")


class DummyMeta:
    def __init__(self, data: dict):
        self._data = data

    def model_dump(self):
        return self._data


class DummyDoc:
    def __init__(self, content, metadata=None, doc_id=None):
        self.content = content
        # metadata should mimic a pydantic model with model_dump()
        self.metadata = metadata or DummyMeta({})
        self.doc_id = doc_id


def make_documents(n=2):
    return [DummyDoc(f"doc {i}", metadata=DummyMeta({"asignatura": "x"}), doc_id=str(i)) for i in range(n)]


def test_index_documents_creates_points(monkeypatch):
    # Mock Qdrant client
    mock_q = MagicMock()
    # get_collections used at init
    mock_q.get_collections.return_value = MagicMock(collections=[])
    mock_q.upsert.return_value = None

    monkeypatch.setattr(store_module, "QdrantClient", lambda host, port: mock_q)

    # Mock embedding service to return fixed vectors
    monkeypatch.setattr(store_module, "get_embedding_service", lambda: MagicMock(embed_documents=lambda texts: [[0.1]*3 for _ in texts]))

    # Mock document processor to skip chunking (return documents unchanged)
    monkeypatch.setitem(store_module.__dict__, "get_document_processor", lambda: MagicMock(chunk_documents=lambda docs: docs))

    svc = store_module.VectorStoreService()
    docs = make_documents(3)
    count = svc.index_documents(docs)
    assert count == 3
    # upsert should have been called once
    mock_q.upsert.assert_called_once()


def test_search_returns_results(monkeypatch):
    mock_q = MagicMock()
    mock_q.get_collections.return_value = MagicMock(collections=[MagicMock(name="c")])

    # Simulate search returning objects with payload and score
    class Res:
        def __init__(self, payload, score):
            self.payload = payload
            self.score = score

    mock_q.search.return_value = [Res({"content": "hello", "asignatura": "x"}, 0.9)]

    monkeypatch.setattr(store_module, "QdrantClient", lambda host, port: mock_q)
    monkeypatch.setattr(emb_module, "get_embedding_service", lambda: MagicMock(embed_query=lambda q: [0.1, 0.2, 0.3]))

    svc = store_module.VectorStoreService()
    results = svc.search("hello")
    assert len(results) == 1
    assert results[0].content == "hello"


def test_get_collection_info_and_delete(monkeypatch):
    mock_q = MagicMock()
    mock_q.get_collections.return_value = MagicMock(collections=[MagicMock(name="c")])
    mock_q.get_collection.return_value = MagicMock(vectors_count=0, points_count=1, status="green")

    monkeypatch.setattr(store_module, "QdrantClient", lambda host, port: mock_q)
    monkeypatch.setattr(emb_module, "get_embedding_service", lambda: MagicMock())

    svc = store_module.VectorStoreService()
    info = svc.get_collection_info()
    assert info["name"] == svc.collection_name

    # delete_collection should call client.delete_collection
    svc.delete_collection()
    mock_q.delete_collection.assert_called_once_with(collection_name=svc.collection_name)
