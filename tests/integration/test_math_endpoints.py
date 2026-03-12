"""
Integration tests for math_service API endpoints.

Tests the full flow through API endpoints using TestClient,
with mocked service dependencies for end-to-end validation.
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from math_service.api import app

client = TestClient(app)

pytestmark = pytest.mark.integration


def _make_faq_service_mock(
    questions: list[str] | None = None,
    faqs: list[dict] | None = None,
):
    """Create a configured FAQService mock."""
    mock = MagicMock()

    if questions is not None:
        mock.generate_faqs.return_value = {
            "status": "success",
            "subject": "Math",
            "questions_analyzed": len(questions),
            "clusters_formed": 2,
            "faqs_generated": len(questions),
            "faqs": questions,
        }

    if faqs is not None:
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = faqs
        mock.faq_collection.find.return_value = mock_cursor

    return mock


def _make_topic_service_mock(
    topics: list[dict] | None = None,
    stored: list[dict] | None = None,
):
    """Create a configured TopicService mock."""
    mock = MagicMock()

    if topics is not None:
        mock.extract_topics.return_value = {
            "status": "success",
            "subject": "Math",
            "clusters_formed": len(topics),
            "topics": topics,
            "concept_map": {
                "nodes": [
                    {"id": "Math", "group": "subject", "label": "Math"},
                ]
                + [
                    {"id": t["topic_name"], "group": "topic", "label": t["topic_name"]}
                    for t in topics
                ],
                "links": [
                    {"source": "Math", "target": t["topic_name"], "value": 1.0}
                    for t in topics
                ],
            },
            "doc_topic_matrix": [[0.5, 0.5]] * 3,
            "created_at": "2026-03-13T12:00:00Z",
            "source_chunks": 30,
        }

    if stored is not None:
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = stored
        mock.collection.find.return_value = mock_cursor

    return mock


# ─── FAQ Endpoint Integration Tests ─────────────────────────────────


@patch("math_service.routes.faqs.FAQService")
def test_generate_then_retrieve_faqs(mock_service_cls):
    """Test E2E: POST /faqs/generate → GET /faqs/{subject}."""
    mock_service = _make_faq_service_mock(
        questions=["¿Qué es una derivada?", "¿Cómo integrar?"],
        faqs=[
            {
                "_id": "abc123",
                "question": "¿Qué es una derivada?",
                "answer": "",
                "cluster_size": 10,
                "status": "draft",
            },
            {
                "_id": "def456",
                "question": "¿Cómo integrar?",
                "answer": "",
                "cluster_size": 5,
                "status": "draft",
            },
        ],
    )
    mock_service_cls.return_value = mock_service

    # Step 1: Generate
    gen_response = client.post(
        "/faqs/generate", json={"subject": "Math", "min_cluster_size": 2}
    )
    assert gen_response.status_code == 200
    gen_data = gen_response.json()
    assert gen_data["status"] == "success"
    assert gen_data["faqs_generated"] == 2

    # Step 2: Retrieve
    get_response = client.get("/faqs/Math")
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert len(get_data) == 2
    assert get_data[0]["question"] == "¿Qué es una derivada?"


@patch("math_service.routes.faqs.FAQService")
def test_update_faq(mock_service_cls):
    """Test PUT /faqs/{subject}/{faq_id} updates a FAQ."""
    mock_service = MagicMock()
    mock_update_result = MagicMock()
    mock_update_result.matched_count = 1
    mock_service.faq_collection.update_one.return_value = mock_update_result
    mock_service_cls.return_value = mock_service

    response = client.put(
        "/faqs/Math/507f1f77bcf86cd799439011",
        json={"question": "Updated question?", "answer": "New answer"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    mock_service.faq_collection.update_one.assert_called_once()


@patch("math_service.routes.faqs.FAQService")
def test_update_faq_not_found(mock_service_cls):
    """Test PUT returns 404 when FAQ doesn't exist."""
    mock_service = MagicMock()
    mock_update_result = MagicMock()
    mock_update_result.matched_count = 0
    mock_service.faq_collection.update_one.return_value = mock_update_result
    mock_service_cls.return_value = mock_service

    response = client.put(
        "/faqs/Math/507f1f77bcf86cd799439011",
        json={"question": "Nonexistent"},
    )

    assert response.status_code == 404


@patch("math_service.routes.faqs.FAQService")
def test_publish_unpublish_faq(mock_service_cls):
    """Test PATCH publish/unpublish endpoints."""
    mock_service = MagicMock()
    mock_result = MagicMock()
    mock_result.matched_count = 1
    mock_service.faq_collection.update_one.return_value = mock_result
    mock_service_cls.return_value = mock_service

    # Publish
    pub_response = client.patch("/faqs/Math/507f1f77bcf86cd799439011/publish")
    assert pub_response.status_code == 200
    assert "published" in pub_response.json()["message"]

    # Unpublish
    unpub_response = client.patch("/faqs/Math/507f1f77bcf86cd799439011/unpublish")
    assert unpub_response.status_code == 200
    assert "unpublished" in unpub_response.json()["message"]


@patch("math_service.routes.faqs.FAQService")
def test_delete_faq(mock_service_cls):
    """Test DELETE /faqs/{subject}/{faq_id}."""
    mock_service = MagicMock()
    mock_delete_result = MagicMock()
    mock_delete_result.deleted_count = 1
    mock_service.faq_collection.delete_one.return_value = mock_delete_result
    mock_service_cls.return_value = mock_service

    response = client.delete("/faqs/Math/507f1f77bcf86cd799439011")
    assert response.status_code == 200
    assert "deleted" in response.json()["message"]


@patch("math_service.routes.faqs.FAQService")
def test_delete_faq_not_found(mock_service_cls):
    """Test DELETE returns 404 when FAQ doesn't exist."""
    mock_service = MagicMock()
    mock_delete_result = MagicMock()
    mock_delete_result.deleted_count = 0
    mock_service.faq_collection.delete_one.return_value = mock_delete_result
    mock_service_cls.return_value = mock_service

    response = client.delete("/faqs/Math/507f1f77bcf86cd799439011")
    assert response.status_code == 404


@patch("math_service.routes.faqs.FAQService")
def test_faq_invalid_id(mock_service_cls):
    """Test that invalid ObjectId returns 400."""
    mock_service = MagicMock()
    mock_service_cls.return_value = mock_service

    response = client.put("/faqs/Math/invalid-id", json={"question": "Test"})
    assert response.status_code == 400
    assert "Invalid FAQ ID" in response.json()["detail"]


# ─── Topics Endpoint Integration Tests ──────────────────────────────


@patch("math_service.routes.topics.TopicService")
def test_extract_then_retrieve_topics(mock_service_cls):
    """Test E2E: POST /topics/extract → GET /topics/{subject}."""
    topics_data = [
        {
            "cluster": 0,
            "topic_name": "Álgebra Lineal",
            "terms": ["matrices", "vectores", "determinantes"],
            "weight": 0.6,
        },
        {
            "cluster": 1,
            "topic_name": "Cálculo",
            "terms": ["derivadas", "integrales", "límites"],
            "weight": 0.4,
        },
    ]
    stored_data = [
        {
            "_id": "stored1",
            "subject": "Math",
            "topics": topics_data,
            "created_at": "2026-03-13T12:00:00Z",
        }
    ]
    mock_service = _make_topic_service_mock(topics=topics_data, stored=stored_data)
    mock_service_cls.return_value = mock_service

    # Step 1: Extract
    ext_response = client.post(
        "/topics/extract",
        json={"subject": "Math", "vectorizer_type": "tfidf", "k": 2},
    )
    assert ext_response.status_code == 200
    ext_data = ext_response.json()
    assert ext_data["status"] == "success"
    assert ext_data["clusters_formed"] == 2
    assert len(ext_data["topics"]) == 2
    assert ext_data["doc_topic_matrix"] is not None

    # Step 2: Retrieve
    get_response = client.get("/topics/Math")
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert len(get_data) == 1
    assert get_data[0]["subject"] == "Math"


@patch("math_service.routes.topics.TopicService")
def test_extract_topics_service_error(mock_service_cls):
    """Test that service error returns HTTP 500."""
    mock_service = MagicMock()
    mock_service.extract_topics.return_value = {
        "status": "error",
        "message": "No chunks found for subject",
    }
    mock_service_cls.return_value = mock_service

    response = client.post("/topics/extract", json={"subject": "Invalid"})

    assert response.status_code == 500
    assert "No chunks found" in response.json()["detail"]


@patch("math_service.routes.topics.TopicService")
def test_get_topics_empty_result(mock_service_cls):
    """Test retrieving topics when no extractions exist."""
    mock_service = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.sort.return_value = []
    mock_service.collection.find.return_value = mock_cursor
    mock_service_cls.return_value = mock_service

    response = client.get("/topics/Nonexistent")

    assert response.status_code == 200
    assert response.json() == []
