from unittest.mock import AsyncMock, MagicMock, patch


@patch("backend.routers.topics.httpx.AsyncClient")
def test_extract_topics_success(mock_client_cls, client, professor_token):
    mock_instance = AsyncMock()
    mock_client_cls.return_value.__aenter__.return_value = mock_instance

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success", "clusters_formed": 5}
    mock_instance.post.return_value = mock_response

    response = client.post(
        "/professor/subjects/iv/topics/extract",
        json={"vectorizer_type": "tfidf"},
        headers={"Authorization": f"Bearer {professor_token}"},
    )
    assert response.status_code == 200
    assert response.json()["clusters_formed"] == 5
    mock_instance.post.assert_awaited_once()


@patch("backend.routers.topics.httpx.AsyncClient")
def test_get_topics_success(mock_client_cls, client, professor_token):
    mock_instance = AsyncMock()
    mock_client_cls.return_value.__aenter__.return_value = mock_instance

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"topics": [{"topic_name": "test"}]}]
    mock_instance.get.return_value = mock_response

    # Prof accessing iv config
    response = client.get(
        "/professor/subjects/iv/topics",
        headers={"Authorization": f"Bearer {professor_token}"},
    )
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_topics_forbidden_subject(client, professor_token):
    # Prof accessing a subject they do not teach
    response = client.get(
        "/professor/subjects/tfg/topics",
        headers={"Authorization": f"Bearer {professor_token}"},
    )
    assert response.status_code == 403
    assert "don't teach this subject" in response.json()["detail"]
