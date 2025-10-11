"""
Tests para verificar el funcionamiento del contenedor vLLM.
Estos tests verifican que el servicio vLLM está corriendo correctamente
y puede procesar solicitudes de chat y tool calling.
"""
import pytest
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_URL = "http://localhost:" + os.getenv("VLLM_MAIN_PORT", "8000")
MAIN_VLLM_MODEL_NAME = os.getenv("MODEL_PATH", "/models/unsloth--mistral-7b-instruct-v0.3-bnb-4bit") 


def test_health_endpoint():
    """Verifica que el endpoint de health del vLLM responde correctamente."""
    resp = requests.get(f"{API_URL}/health")
    assert resp.status_code == 200


def test_chat_completions():
    """Verifica que el vLLM puede procesar completions de chat básicas."""
    payload = {
        "model": MAIN_VLLM_MODEL_NAME,
        "messages": [
            {"role": "user", "content": "Hola, ¿cómo estás?"}
        ]
    }
    resp = requests.post(f"{API_URL}/v1/chat/completions", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "choices" in data
    assert len(data["choices"]) > 0
    assert "message" in data["choices"][0]


def test_tool_calling():
    """Verifica que el vLLM puede realizar tool calling correctamente."""
    # Definir las herramientas disponibles
    tools = [
        {
            "type": "function",
            "function": {
                "name": "consultar_tiempo",
                "description": "Devuelve el tiempo que hace en un lugar",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lugar": {
                            "type": "string",
                            "description": "Ciudad. ej. Granada"
                        },
                        "unidad": {
                            "type": "string",
                            "enum": ["celcius", "fahrenheit"],
                            "description": "Unidad de temperatura"
                        }
                    },
                    "required": ["lugar"]
                }
            }
        }
    ]

    payload = {
        "model": MAIN_VLLM_MODEL_NAME,
        "messages": [
            {
                "role": "user", 
                "content": "Qué tiempo hace tiempo hoy en Málaga?"
            }
        ],
        "tools": tools,
        "tool_choice": "auto",
        "max_tokens": 150
    }
    # Llamada que debería activar tool calling
    requests.post(f"{API_URL}/v1/chat/completions", json=payload)

    resp = requests.post(f"{API_URL}/v1/chat/completions", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "choices" in data
    assert len(data["choices"]) > 0
    # Verifica que la respuesta contiene una llamada a herramienta
    assert "tool_calls" in data["choices"][0]["message"]


def test_invalid_model():
    """Verifica que el vLLM rechaza modelos inexistentes."""
    payload = {
        "model": "modelo-inexistente",
        "messages": [{"role": "user", "content": "Hola"}],
        "max_tokens": 10
    }
    response = requests.post(f"{API_URL}/v1/chat/completions", json=payload)
    assert response.status_code == 400 or response.status_code == 404


def test_invalid_message_format():
    """Verifica que el vLLM valida el formato de los mensajes."""
    payload = {
        "model": "tu-modelo",
        "messages": [{"content": "Hola"}],  # Falta 'role'
        "max_tokens": 10
    }
    response = requests.post(f"{API_URL}/v1/chat/completions", json=payload)
    assert response.status_code == 400


def test_invalid_tool_definition():
    """Verifica que el vLLM valida las definiciones de herramientas."""
    payload = {
        "model": "tu-modelo",
        "messages": [{"role": "user", "content": "¿Qué tiempo hace?"}],
        "tools": [{"type": "function"}],  # Falta 'function' details
        "max_tokens": 10
    }
    response = requests.post(f"{API_URL}/v1/chat/completions", json=payload)
    assert response.status_code == 400
