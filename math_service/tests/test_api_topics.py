from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from math_service.api import app

client = TestClient(app)


@patch("math_service.routes.topics.TopicService")
def test_extract_topics_success(mock_service_cls):
    """Test extracting topics successfully."""
    mock_service_instance = MagicMock()
    mock_service_cls.return_value = mock_service_instance

    mock_service_instance.extract_topics.return_value = {
        "status": "success",
        "subject": "Math",
        "clusters_formed": 2,
        "topics": [
            {
                "cluster": 0,
                "topic_name": "Tópico 1",
                "terms": ["algebra", "equations"],
                "weight": 0.5,
            }
        ],
        "concept_map": {
            "nodes": [
                {"id": "Math", "group": "subject", "label": "Math"},
                {"id": "Tópico 1", "group": "topic", "label": "Tópico 1"},
            ],
            "links": [{"source": "Math", "target": "Tópico 1", "value": 1.0}],
        },
        "created_at": "2026-03-04T12:00:00Z",
        "source_chunks": 50,
    }

    response = client.post(
        "/topics/extract", json={"subject": "Math", "vectorizer_type": "tfidf"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["subject"] == "Math"
    assert data["clusters_formed"] == 2
    assert len(data["topics"]) == 1
    assert data["concept_map"]["nodes"][0]["id"] == "Math"

    mock_service_instance.extract_topics.assert_called_once_with(
        subject="Math", vectorizer_type="tfidf"
    )
    mock_service_instance.close.assert_called_once()


@patch("math_service.routes.topics.TopicService")
def test_extract_topics_error(mock_service_cls):
    """Test extracting topics when service returns an error."""
    mock_service_instance = MagicMock()
    mock_service_cls.return_value = mock_service_instance

    mock_service_instance.extract_topics.return_value = {
        "status": "error",
        "message": "No chunks found",
    }

    response = client.post("/topics/extract", json={"subject": "Invalid"})

    assert response.status_code == 500
    data = response.json()
    assert data["detail"] == "No chunks found"
    mock_service_instance.close.assert_called_once()


@patch("math_service.routes.topics.TopicService")
def test_get_topics_by_subject(mock_service_cls):
    """Test retrieving existing topic extractions."""
    mock_service_instance = MagicMock()
    mock_service_cls.return_value = mock_service_instance

    mock_cursor = MagicMock()
    mock_cursor.sort.return_value = [{"subject": "Math", "topics": []}]
    mock_service_instance.collection.find.return_value = mock_cursor

    response = client.get("/topics/Math")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["subject"] == "Math"

    mock_service_instance.collection.find.assert_called_once_with(
        {"subject": "Math"}, {"_id": 0}
    )
    mock_service_instance.close.assert_called_once()
