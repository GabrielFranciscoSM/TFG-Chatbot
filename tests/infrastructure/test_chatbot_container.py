"""
Tests para verificar el funcionamiento del contenedor del chatbot.
"""

import os

import pytest
import requests

# Chatbot runs on port 8080 as per docker-compose.yml
CHATBOT_URL = os.getenv("CHATBOT_URL", "http://localhost:8080")


def test_chatbot_container_is_running():
    """Verifica que el contenedor del chatbot está corriendo y responde."""
    try:
        resp = requests.get(f"{CHATBOT_URL}/health", timeout=5)
        assert resp.status_code == 200
        assert resp.json() == {"message": "Hello World"}
    except requests.exceptions.ConnectionError:
        pytest.fail(f"El contenedor del chatbot no está disponible en {CHATBOT_URL}")


def test_chatbot_container_root_endpoint():
    """Verifica que el endpoint raíz del chatbot funciona correctamente."""
    resp = requests.get(f"{CHATBOT_URL}/", timeout=5)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "TFG Chatbot API"
    assert data["status"] == "running"


def test_chatbot_container_accepts_chat_requests():
    """Verifica que el chatbot acepta y procesa requests de chat básicos."""
    payload = {"query": "Hola", "id": "test-container-session"}
    # Aumentar timeout porque el LLM puede tardar en responder
    try:
        resp = requests.post(f"{CHATBOT_URL}/chat", json=payload, timeout=60)

        if resp.status_code == 503:
            pytest.skip("Chatbot service unavailable (503) - LLM might be down")

        assert resp.status_code == 200
        data = resp.json()

        # Verificar estructura de la respuesta (nuevo formato)
        assert "message" in data
        assert "content" in data["message"]
        assert data["message"]["type"] == "ai"

    except requests.exceptions.ReadTimeout:
        pytest.fail("Timeout waiting for chatbot response")
