import uuid

import pytest
import requests


@pytest.fixture(scope="module")
def auth_token(api_base_url):
    """Registra un usuario y devuelve un token válido para los tests."""
    username = f"integration_user_{uuid.uuid4()}"
    password = "testpassword"
    email = f"{username}@example.com"

    # 1. Register
    register_payload = {
        "username": username,
        "password": password,
        "email": email,
        "role": "student",
        "subjects": ["iv"],
    }
    resp = requests.post(f"{api_base_url}/register", json=register_payload, timeout=5)
    assert resp.status_code == 200

    # 2. Login
    login_payload = {"username": username, "password": password}
    resp = requests.post(f"{api_base_url}/token", data=login_payload, timeout=5)
    assert resp.status_code == 200

    return resp.json()["access_token"]


@pytest.mark.integration
def test_chat_endpoint_basic_conversation(
    api_base_url, session_id, api_timeout, auth_token
):
    """Test básico de conversación con el chatbot a través de la API."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    payload = {"query": "Hola, ¿cómo estás?", "id": session_id, "asignatura": "iv"}

    response = requests.post(
        f"{api_base_url}/chat", json=payload, headers=headers, timeout=api_timeout
    )
    assert response.status_code == 200

    result = response.json()
    assert "message" in result
    assert "content" in result["message"]


@pytest.mark.integration
def test_chat_endpoint_with_tools(api_base_url, session_id, api_timeout, auth_token):
    """Test que verifica que el chatbot puede usar herramientas a través de la API."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    payload = {"query": "¿Cuánto es 2 + 2?", "id": session_id, "asignatura": "iv"}

    response = requests.post(
        f"{api_base_url}/chat", json=payload, headers=headers, timeout=api_timeout
    )
    assert response.status_code == 200

    result = response.json()
    assert "message" in result
    assert "content" in result["message"]
    assert "4" in result["message"]["content"]


@pytest.mark.integration
def test_chat_endpoint_with_memory(api_base_url, session_id, api_timeout, auth_token):
    """Test que verifica que el chatbot mantiene memoria de la conversación."""
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Primera interacción
    payload_1 = {"query": "Mi nombre es Alicia", "id": session_id, "asignatura": "iv"}
    response_1 = requests.post(
        f"{api_base_url}/chat", json=payload_1, headers=headers, timeout=api_timeout
    )
    assert response_1.status_code == 200
    result_1 = response_1.json()
    assert "message" in result_1

    # Segunda interacción - verificar que recuerda el nombre
    payload_2 = {"query": "¿Cuál es mi nombre?", "id": session_id, "asignatura": "iv"}
    response_2 = requests.post(
        f"{api_base_url}/chat", json=payload_2, headers=headers, timeout=api_timeout
    )
    assert response_2.status_code == 200
    result_2 = response_2.json()
    assert "message" in result_2
    assert "content" in result_2["message"]
    assert "Alicia" in result_2["message"]["content"]


@pytest.mark.integration
def test_chat_endpoint_empty_message(api_base_url, session_id, api_timeout, auth_token):
    """Test que verifica el comportamiento con mensajes vacíos."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    payload = {"query": "", "id": session_id, "asignatura": "iv"}

    response = requests.post(
        f"{api_base_url}/chat", json=payload, headers=headers, timeout=api_timeout
    )
    # Con el nuevo formato, mensajes vacíos pueden devolver 200 con respuesta del LLM
    assert response.status_code in [200, 500, 422, 400]


@pytest.mark.integration
def test_chat_endpoint_invalid_payload(api_base_url, api_timeout, auth_token):
    """Test que verifica el manejo de payloads inválidos."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    # Payload sin campo requerido
    invalid_payload = {
        "query": "Hola"
        # Falta el campo 'id'
    }

    response = requests.post(
        f"{api_base_url}/chat",
        json=invalid_payload,
        headers=headers,
        timeout=api_timeout,
    )
    assert response.status_code == 422  # Unprocessable Entity


@pytest.mark.integration
def test_chat_endpoint_different_sessions(
    api_base_url, session_id, api_timeout, auth_token
):
    """Test que verifica que diferentes sesiones mantienen contextos separados."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    session_id_2 = f"test-session-different-{session_id}"

    # Primera sesión - establecer nombre
    payload_1 = {"query": "Mi nombre es Roberto", "id": session_id, "asignatura": "iv"}
    requests.post(
        f"{api_base_url}/chat", json=payload_1, headers=headers, timeout=api_timeout
    )

    # Segunda sesión - establecer nombre diferente
    payload_2 = {
        "query": "Mi nombre es Carolina",
        "id": session_id_2,
        "asignatura": "iv",
    }
    requests.post(
        f"{api_base_url}/chat", json=payload_2, headers=headers, timeout=api_timeout
    )

    # Verificar primera sesión
    payload_verify_1 = {
        "query": "¿Cuál es mi nombre?",
        "id": session_id,
        "asignatura": "iv",
    }
    response_1 = requests.post(
        f"{api_base_url}/chat",
        json=payload_verify_1,
        headers=headers,
        timeout=api_timeout,
    )
    result_1 = response_1.json()
    assert "message" in result_1
    assert "Roberto" in result_1["message"]["content"]

    # Verificar segunda sesión
    payload_verify_2 = {
        "query": "¿Cuál es mi nombre?",
        "id": session_id_2,
        "asignatura": "iv",
    }
    response_2 = requests.post(
        f"{api_base_url}/chat",
        json=payload_verify_2,
        headers=headers,
        timeout=api_timeout,
    )
    result_2 = response_2.json()
    assert "message" in result_2
    assert "Carolina" in result_2["message"]["content"]


@pytest.mark.integration
def test_chat_endpoint_forbidden_subject(
    api_base_url, session_id, api_timeout, auth_token
):
    """Test que verifica que no se puede acceder a una asignatura no matriculada."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    payload = {
        "query": "Hola",
        "id": session_id,
        "asignatura": "tfg",  # Usuario matriculado en 'iv'
    }

    response = requests.post(
        f"{api_base_url}/chat", json=payload, headers=headers, timeout=api_timeout
    )
    assert response.status_code == 403
