"""
Tests para verificar el funcionamiento del contenedor del backend (Gateway/Auth).
"""

import uuid

import pytest
import requests

from tests.infrastructure.conftest import BACKEND_URL, DEFAULT_TIMEOUT, LLM_TIMEOUT

# Aplicar marker a todos los tests de este módulo
pytestmark = pytest.mark.podman_container


def _register_user(username: str, password: str, email: str) -> dict:
    """
    Helper para registrar un usuario.

    Args:
        username: Nombre de usuario.
        password: Contraseña.
        email: Email del usuario.

    Returns:
        Datos del usuario registrado.
    """
    register_payload = {
        "username": username,
        "password": password,
        "email": email,
        "role": "student",
        "subjects": ["iv"],
    }
    resp = requests.post(
        f"{BACKEND_URL}/register", json=register_payload, timeout=DEFAULT_TIMEOUT
    )
    return resp.json() if resp.status_code == 200 else {}


def get_auth_token() -> str:
    """
    Helper para obtener un token válido para tests.

    Returns:
        Token de acceso JWT.
    """
    username = f"testuser_{uuid.uuid4()}"
    password = "testpassword"
    email = f"{username}@example.com"

    _register_user(username, password, email)

    login_payload = {"username": username, "password": password}
    resp = requests.post(
        f"{BACKEND_URL}/token", data=login_payload, timeout=DEFAULT_TIMEOUT
    )
    return resp.json()["access_token"]


def test_backend_container_is_running():
    """Verifica que el contenedor del backend está corriendo y responde."""
    try:
        resp = requests.get(f"{BACKEND_URL}/health", timeout=DEFAULT_TIMEOUT)
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}
    except requests.exceptions.ConnectionError:
        pytest.fail(f"El contenedor del backend no está disponible en {BACKEND_URL}")


def test_backend_auth_flow():
    """Verifica el flujo de registro y login."""
    username = f"testuser_{uuid.uuid4()}"
    password = "testpassword"
    email = f"{username}@example.com"

    # 1. Registrar
    data = _register_user(username, password, email)
    assert data["username"] == username
    assert "hashed_password" not in data

    # 2. Login
    login_payload = {"username": username, "password": password}
    resp = requests.post(
        f"{BACKEND_URL}/token", data=login_payload, timeout=DEFAULT_TIMEOUT
    )
    assert resp.status_code == 200
    token_data = resp.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"


def test_backend_chat_endpoint_requires_auth():
    """Verifica que el endpoint de chat requiere autenticación."""
    resp = requests.post(
        f"{BACKEND_URL}/chat", json={"query": "Hola"}, timeout=DEFAULT_TIMEOUT
    )
    assert resp.status_code == 401


def test_backend_chat_flow():
    """Verifica el flujo completo de chat con autenticación."""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    session_id = f"test-container-{uuid.uuid4()}"
    payload = {"query": "Hola", "asignatura": "iv", "id": session_id}

    try:
        resp = requests.post(
            f"{BACKEND_URL}/chat", json=payload, headers=headers, timeout=LLM_TIMEOUT
        )

        # Si el chatbot no está disponible, skip el test
        if resp.status_code in [503, 500]:
            pytest.skip("Chatbot service might not be available")

        assert resp.status_code == 200
        data = resp.json()

        # Verificar estructura de la respuesta
        assert "message" in data
        assert "content" in data["message"]

    except requests.exceptions.ReadTimeout:
        pytest.fail("Timeout waiting for chat response")
