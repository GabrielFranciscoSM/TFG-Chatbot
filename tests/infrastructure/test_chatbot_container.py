"""
Tests para verificar el funcionamiento del contenedor del chatbot.
"""

import pytest
import requests

from tests.infrastructure.conftest import CHATBOT_URL, DEFAULT_TIMEOUT, LLM_TIMEOUT

# Aplicar marker a todos los tests de este módulo
pytestmark = pytest.mark.podman_container


def test_chatbot_container_is_running():
    """Verifica que el contenedor del chatbot está corriendo y responde."""
    try:
        resp = requests.get(f"{CHATBOT_URL}/health", timeout=DEFAULT_TIMEOUT)
        assert resp.status_code == 200
        assert resp.json() == {"message": "Hello World"}
    except requests.exceptions.ConnectionError:
        pytest.fail(f"El contenedor del chatbot no está disponible en {CHATBOT_URL}")


def test_chatbot_container_root_endpoint():
    """Verifica que el endpoint raíz del chatbot funciona correctamente."""
    resp = requests.get(f"{CHATBOT_URL}/", timeout=DEFAULT_TIMEOUT)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "TFG Chatbot API"
    assert data["status"] == "running"


def test_chatbot_container_accepts_chat_requests():
    """Verifica que el chatbot acepta y procesa requests de chat básicos."""
    payload = {"query": "Hola", "id": "test-container-session"}

    try:
        resp = requests.post(f"{CHATBOT_URL}/chat", json=payload, timeout=LLM_TIMEOUT)

        if resp.status_code == 503:
            pytest.skip("Chatbot service unavailable (503) - LLM might be down")

        assert resp.status_code == 200
        data = resp.json()

        # Verificar estructura de la respuesta
        assert "message" in data
        assert "content" in data["message"]
        assert data["message"]["type"] == "ai"

    except requests.exceptions.ReadTimeout:
        pytest.fail("Timeout waiting for chatbot response")
