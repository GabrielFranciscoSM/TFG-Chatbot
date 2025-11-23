from unittest.mock import AsyncMock, MagicMock, patch


@patch("backend.routers.chat.httpx.AsyncClient")
def test_chat_allowed_subject(mock_client_cls, client, student_token):
    # Setup mock
    mock_instance = AsyncMock()
    mock_client_cls.return_value = mock_instance
    mock_instance.__aenter__.return_value = mock_instance

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"response": "Hello from AI"}

    mock_instance.post.return_value = mock_response

    response = client.post(
        "/chat",
        json={"query": "hello", "asignatura": "iv"},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert response.status_code == 200
    assert response.json()["response"] == "Hello from AI"


def test_chat_forbidden_subject(client, student_token):
    # Student is enrolled in 'iv', but tries to access 'tfg'
    response = client.post(
        "/chat",
        json={"query": "hello", "asignatura": "tfg"},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert response.status_code == 403
    assert "Not enrolled" in response.json()["detail"]


@patch("backend.routers.chat.httpx.AsyncClient")
def test_chat_professor_any_subject(mock_client_cls, client, professor_token):
    # Setup mock
    mock_instance = AsyncMock()
    mock_client_cls.return_value = mock_instance
    mock_instance.__aenter__.return_value = mock_instance

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"response": "Hello Prof"}

    mock_instance.post.return_value = mock_response

    response = client.post(
        "/chat",
        json={"query": "hello", "asignatura": "random_subject"},
        headers={"Authorization": f"Bearer {professor_token}"},
    )
    assert response.status_code == 200
