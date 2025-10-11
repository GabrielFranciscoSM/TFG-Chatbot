"""
Tests para verificar el funcionamiento del contenedor del backend (FastAPI).
Estos tests son unitarios básicos que verifican que el contenedor está corriendo
y responde correctamente a las peticiones HTTP.
"""
import pytest
import requests


BACKEND_URL = "http://localhost:8080"


def test_backend_container_is_running():
    """Verifica que el contenedor del backend está corriendo y responde."""
    try:
        resp = requests.get(f"{BACKEND_URL}/health", timeout=5)
        assert resp.status_code == 200
        assert resp.json() == {"message": "Hello World"}
    except requests.exceptions.ConnectionError:
        pytest.fail("El contenedor del backend no está disponible en http://localhost:8080")


def test_backend_container_root_endpoint():
    """Verifica que el endpoint raíz del backend funciona correctamente."""
    resp = requests.get(f"{BACKEND_URL}/", timeout=5)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "TFG Chatbot API"
    assert data["status"] == "running"
    assert "endpoints" in data


def test_backend_container_accepts_chat_requests():
    """Verifica que el backend acepta y procesa requests de chat básicos."""
    payload = {
        "query": "Hola",
        "id": "test-container-session"
    }
    # Aumentar timeout porque el LLM puede tardar en responder
    resp = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=60)
    assert resp.status_code == 200
    data = resp.json()
    
    # Verificar estructura de la respuesta
    assert "messages" in data
    assert isinstance(data["messages"], list)
    assert len(data["messages"]) > 0
    
    # Verificar que hay al menos el mensaje del usuario
    assert any(msg.get("type") == "human" for msg in data["messages"])
    # Verificar que hay una respuesta del agente
    assert any(msg.get("type") == "ai" for msg in data["messages"])


def test_backend_container_validates_payload():
    """Verifica que el backend valida correctamente los payloads."""
    # Payload sin campo 'id' requerido
    invalid_payload = {
        "query": "Hola"
    }
    resp = requests.post(f"{BACKEND_URL}/chat", json=invalid_payload, timeout=5)
    assert resp.status_code == 422  # Unprocessable Entity
    
    # Payload sin campo 'query' requerido
    invalid_payload_2 = {
        "id": "test-session"
    }
    resp2 = requests.post(f"{BACKEND_URL}/chat", json=invalid_payload_2, timeout=5)
    assert resp2.status_code == 422
    
    # Payload completamente vacío
    resp3 = requests.post(f"{BACKEND_URL}/chat", json={}, timeout=5)
    assert resp3.status_code == 422
