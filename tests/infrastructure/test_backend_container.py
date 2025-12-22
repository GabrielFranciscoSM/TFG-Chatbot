"""
Tests para verificar el funcionamiento del contenedor del backend (Gateway/Auth).
"""

import os
import uuid

import pytest
import requests

# Backend runs on port 8000 as per docker-compose.yml
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


def test_backend_container_is_running():
    """Verifica que el contenedor del backend está corriendo y responde."""
    try:
        resp = requests.get(f"{BACKEND_URL}/health", timeout=5)
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}
    except requests.exceptions.ConnectionError:
        pytest.fail(f"El contenedor del backend no está disponible en {BACKEND_URL}")


def test_backend_auth_flow():
    """Verifica el flujo de registro y login."""
    username = f"testuser_{uuid.uuid4()}"
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
    resp = requests.post(f"{BACKEND_URL}/register", json=register_payload, timeout=5)
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == username
    assert "hashed_password" not in data

    # 2. Login
    login_payload = {"username": username, "password": password}
    resp = requests.post(f"{BACKEND_URL}/token", data=login_payload, timeout=5)
    assert resp.status_code == 200
    token_data = resp.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

    # return token_data["access_token"]  <-- Removed return to avoid pytest warning


def get_auth_token():
    """Helper function to get a valid token for other tests."""
    username = f"testuser_{uuid.uuid4()}"
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
    requests.post(f"{BACKEND_URL}/register", json=register_payload, timeout=5)

    # 2. Login
    login_payload = {"username": username, "password": password}
    resp = requests.post(f"{BACKEND_URL}/token", data=login_payload, timeout=5)
    return resp.json()["access_token"]


def test_backend_chat_endpoint_requires_auth():
    """Verifica que el endpoint de chat requiere autenticación."""
    resp = requests.post(f"{BACKEND_URL}/chat", json={"query": "Hola"}, timeout=5)
    assert resp.status_code == 401


def test_backend_chat_flow():
    """Verifica el flujo completo de chat con autenticación."""
    # Get a fresh token
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Use unique session ID to avoid conflicts with previous test runs
    session_id = f"test-container-{uuid.uuid4()}"
    payload = {"query": "Hola", "asignatura": "iv", "id": session_id}

    # Aumentar timeout porque el LLM puede tardar en responder
    # Nota: Esto fallará si el servicio de chatbot no está corriendo o mockeado
    try:
        resp = requests.post(
            f"{BACKEND_URL}/chat", json=payload, headers=headers, timeout=60
        )

        # Si el chatbot no está disponible, podríamos recibir un 500 o 503
        if resp.status_code == 503 or resp.status_code == 500:
            pytest.skip("Chatbot service might not be available")

        assert resp.status_code == 200
        data = resp.json()

        # Verificar estructura de la respuesta (nuevo formato)
        assert "message" in data
        assert "content" in data["message"]

    except requests.exceptions.ReadTimeout:
        pytest.fail("Timeout waiting for chat response")
