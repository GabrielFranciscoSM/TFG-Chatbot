from unittest.mock import AsyncMock, MagicMock, patch


@patch("backend.routers.faqs.httpx.AsyncClient")
def test_generate_faqs_success(mock_client_cls, client, professor_token):
    mock_instance = AsyncMock()
    mock_client_cls.return_value.__aenter__.return_value = mock_instance

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success", "faqs_generated": 2}
    mock_instance.post.return_value = mock_response

    response = client.post(
        "/professor/subjects/iv/faqs/generate",
        json={"min_cluster_size": 2},
        headers={"Authorization": f"Bearer {professor_token}"},
    )
    assert response.status_code == 200
    assert response.json()["faqs_generated"] == 2
    mock_instance.post.assert_awaited_once()


@patch("backend.routers.faqs.httpx.AsyncClient")
def test_create_faq_success(mock_client_cls, client, professor_token):
    mock_instance = AsyncMock()
    mock_client_cls.return_value.__aenter__.return_value = mock_instance

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": "1", "question": "test?"}
    mock_instance.post.return_value = mock_response

    response = client.post(
        "/professor/subjects/iv/faqs",
        json={"question": "test?", "answer": "", "status": "draft"},
        headers={"Authorization": f"Bearer {professor_token}"},
    )
    assert response.status_code == 200
    assert response.json()["question"] == "test?"
    mock_instance.post.assert_awaited_once()


@patch("backend.routers.faqs.httpx.AsyncClient")
def test_get_professor_faqs(mock_client_cls, client, professor_token):
    mock_instance = AsyncMock()
    mock_client_cls.return_value.__aenter__.return_value = mock_instance

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"question": "test?", "status": "draft"}]
    mock_instance.get.return_value = mock_response

    response = client.get(
        "/professor/subjects/iv/faqs",
        headers={"Authorization": f"Bearer {professor_token}"},
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["question"] == "test?"


def test_faqs_forbidden_subject(client, professor_token):
    # Professor tries to access 'tfg' which they don't teach
    response = client.get(
        "/professor/subjects/tfg/faqs",
        headers={"Authorization": f"Bearer {professor_token}"},
    )
    assert response.status_code == 403
    assert "don't teach this subject" in response.json()["detail"]


@patch("backend.routers.faqs.httpx.AsyncClient")
def test_update_faq(mock_client_cls, client, professor_token):
    mock_instance = AsyncMock()
    mock_client_cls.return_value.__aenter__.return_value = mock_instance

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success"}
    mock_instance.put.return_value = mock_response

    response = client.put(
        "/professor/subjects/iv/faqs/123",
        json={"answer": "42"},
        headers={"Authorization": f"Bearer {professor_token}"},
    )
    assert response.status_code == 200


@patch("backend.routers.faqs.httpx.AsyncClient")
def test_publish_faq(mock_client_cls, client, professor_token):
    mock_instance = AsyncMock()
    mock_client_cls.return_value.__aenter__.return_value = mock_instance

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success"}
    mock_instance.patch.return_value = mock_response

    response = client.patch(
        "/professor/subjects/iv/faqs/123/publish",
        headers={"Authorization": f"Bearer {professor_token}"},
    )
    assert response.status_code == 200


@patch("backend.routers.faqs.httpx.AsyncClient")
def test_delete_faq(mock_client_cls, client, professor_token):
    mock_instance = AsyncMock()
    mock_client_cls.return_value.__aenter__.return_value = mock_instance

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success"}
    mock_instance.delete.return_value = mock_response

    response = client.delete(
        "/professor/subjects/iv/faqs/123",
        headers={"Authorization": f"Bearer {professor_token}"},
    )
    assert response.status_code == 200


@patch("backend.routers.faqs.httpx.AsyncClient")
def test_get_public_faqs(mock_client_cls, client):
    mock_instance = AsyncMock()
    mock_client_cls.return_value.__aenter__.return_value = mock_instance

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"question": "test1?", "status": "published"},
        {"question": "test2?", "status": "draft"},
    ]
    mock_instance.get.return_value = mock_response

    response = client.get("/subjects/iv/faqs")
    # Should only return published FAQs
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["question"] == "test1?"
