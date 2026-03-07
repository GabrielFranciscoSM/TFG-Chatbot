from unittest.mock import MagicMock, patch

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
        {"question": "What is 1+1?", "cluster_size": 10},
        {"question": "How to do integrals?", "cluster_size": 5},
    ]
    mock_service_instance.faq_collection.find.return_value = mock_cursor

    response = client.get("/faqs/Math")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["question"] == "What is 1+1?"
    assert data[1]["question"] == "How to do integrals?"

    mock_service_instance.faq_collection.find.assert_called_once_with(
        {"subject": "Math"}, {"_id": 0}
    )
    mock_service_instance.close.assert_called_once()
