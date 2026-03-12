from unittest.mock import MagicMock, patch

from bson import ObjectId
from fastapi.testclient import TestClient

from math_service.api import app

client = TestClient(app)


@patch("math_service.routes.faqs.FAQService")
def test_generate_faqs_success(mock_service_cls):
    """Test generating FAQs successfully."""
    mock_service_instance = MagicMock()
    mock_service_cls.return_value = mock_service_instance

    mock_service_instance.generate_faqs.return_value = {
        "status": "success",
        "subject": "Math",
        "questions_analyzed": 10,
        "clusters_formed": 3,
        "faqs_generated": 2,
        "faqs": ["Question 1", "Question 2"],
    }

    response = client.post(
        "/faqs/generate", json={"subject": "Math", "min_cluster_size": 3}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["subject"] == "Math"
    assert data["faqs"] == ["Question 1", "Question 2"]

    mock_service_instance.generate_faqs.assert_called_once_with(
        subject="Math", min_cluster_size=3
    )
    mock_service_instance.close.assert_called_once()


@patch("math_service.routes.faqs.FAQService")
def test_generate_faqs_error(mock_service_cls):
    """Test generating FAQs when service returns an error."""
    mock_service_instance = MagicMock()
    mock_service_cls.return_value = mock_service_instance

    mock_service_instance.generate_faqs.return_value = {
        "status": "error",
        "message": "NLP service unavailable",
    }

    response = client.post("/faqs/generate", json={"subject": "Math"})

    assert response.status_code == 500
    data = response.json()
    assert data["detail"] == "NLP service unavailable"
    mock_service_instance.close.assert_called_once()


@patch("math_service.routes.faqs.FAQService")
def test_get_faqs_by_subject(mock_service_cls):
    """Test retrieving FAQs by subject."""
    mock_service_instance = MagicMock()
    mock_service_cls.return_value = mock_service_instance

    mock_cursor = MagicMock()
    mock_cursor.sort.return_value = [
        {"_id": "1", "question": "What is 1+1?", "cluster_size": 10},
        {"_id": "2", "question": "How to do integrals?", "cluster_size": 5},
    ]
    mock_service_instance.faq_collection.find.return_value = mock_cursor

    response = client.get("/faqs/Math")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["question"] == "What is 1+1?"
    assert data[1]["question"] == "How to do integrals?"

    mock_service_instance.faq_collection.find.assert_called_once_with(
        {"subject": "Math"}
    )
    mock_service_instance.close.assert_called_once()


@patch("math_service.routes.faqs.FAQService")
def test_create_faq_success(mock_service_cls):
    """Test creating a manual FAQ successfully."""
    mock_service_instance = MagicMock()
    mock_service_cls.return_value = mock_service_instance

    inserted_id = ObjectId("65f1a2b3c4d5e6f7a8b9c0d1")
    mock_service_instance.faq_collection.insert_one.return_value.inserted_id = (
        inserted_id
    )

    response = client.post(
        "/faqs/Math",
        json={"question": "What is 1+1?", "answer": "", "status": "draft"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(inserted_id)
    assert data["question"] == "What is 1+1?"
    assert data["answer"] == ""
    assert data["status"] == "draft"
    assert data["subject"] == "Math"
    assert data["cluster_size"] == 0
    assert "created_at" in data
    assert "updated_at" in data

    mock_service_instance.faq_collection.insert_one.assert_called_once()
    mock_service_instance.close.assert_called_once()


@patch("math_service.routes.faqs.FAQService")
def test_create_faq_invalid_status(mock_service_cls):
    """Test creating a manual FAQ with invalid status."""
    mock_service_instance = MagicMock()
    mock_service_cls.return_value = mock_service_instance

    response = client.post(
        "/faqs/Math",
        json={"question": "What is 1+1?", "status": "archived"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid FAQ status"
    mock_service_instance.close.assert_called_once()


@patch("math_service.routes.faqs.FAQService")
def test_create_faq_empty_question(mock_service_cls):
    """Test creating a manual FAQ with an empty question."""
    mock_service_instance = MagicMock()
    mock_service_cls.return_value = mock_service_instance

    response = client.post(
        "/faqs/Math",
        json={"question": "   ", "status": "draft"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Question cannot be empty"
    mock_service_instance.close.assert_called_once()
