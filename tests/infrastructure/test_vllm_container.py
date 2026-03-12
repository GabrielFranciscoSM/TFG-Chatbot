"""
Tests para verificar el funcionamiento del contenedor vLLM.
Estos tests verifican que el servicio vLLM está corriendo correctamente
y puede procesar solicitudes de chat y tool calling.
"""

import os

import pytest
import requests

from tests.infrastructure.conftest import DEFAULT_TIMEOUT, LLM_TIMEOUT, VLLM_MODEL_NAME

# Skip vLLM infra tests unless LLM_PROVIDER is explicitly set to 'vllm'
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "vllm")

# Aplicar markers: container + skipif
pytestmark = [
    pytest.mark.container,
    pytest.mark.skipif(
        LLM_PROVIDER.lower() != "vllm",
        reason="Skipping vLLM infra tests because LLM_PROVIDER != vllm",
    ),
]

# vLLM external port (internal is still 8000)
VLLM_API_URL = os.getenv("VLLM_URL", "http://localhost:8001")


def test_health_endpoint():
    """Verifica que el endpoint de health del vLLM responde correctamente."""
    resp = requests.get(f"{VLLM_API_URL}/health", timeout=DEFAULT_TIMEOUT)
    assert resp.status_code == 200


def test_chat_completions():
    """Verifica que el vLLM puede procesar completions de chat básicas."""
    payload = {
        "model": VLLM_MODEL_NAME,
        "messages": [{"role": "user", "content": "Hola, ¿cómo estás?"}],
    }
    resp = requests.post(
        f"{VLLM_API_URL}/v1/chat/completions", json=payload, timeout=LLM_TIMEOUT
    )
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
                            "description": "Ciudad. ej. Granada",
                        },
                        "unidad": {
                            "type": "string",
                            "enum": ["celcius", "fahrenheit"],
                            "description": "Unidad de temperatura",
                        },
                    },
                    "required": ["lugar"],
                },
            },
        }
    ]

    payload = {
        "model": VLLM_MODEL_NAME,
        "messages": [
            {"role": "user", "content": "Qué tiempo hace tiempo hoy en Málaga?"}
        ],
        "tools": tools,
        "tool_choice": "auto",
        "max_tokens": 150,
    }

    resp = requests.post(
        f"{VLLM_API_URL}/v1/chat/completions", json=payload, timeout=LLM_TIMEOUT
    )
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
        "max_tokens": 10,
    }
    response = requests.post(
        f"{VLLM_API_URL}/v1/chat/completions", json=payload, timeout=DEFAULT_TIMEOUT
    )
    assert response.status_code in [400, 404]


def test_invalid_message_format():
    """Verifica que el vLLM valida el formato de los mensajes."""
    payload = {
        "model": VLLM_MODEL_NAME,
        "messages": [{"content": "Hola"}],  # Falta 'role'
        "max_tokens": 10,
    }
    response = requests.post(
        f"{VLLM_API_URL}/v1/chat/completions", json=payload, timeout=DEFAULT_TIMEOUT
    )
    assert response.status_code == 400


def test_invalid_tool_definition():
    """Verifica que el vLLM valida las definiciones de herramientas."""
    payload = {
        "model": VLLM_MODEL_NAME,
        "messages": [{"role": "user", "content": "¿Qué tiempo hace?"}],
        "tools": [{"type": "function"}],  # Falta 'function' details
        "max_tokens": 10,
    }
    response = requests.post(
        f"{VLLM_API_URL}/v1/chat/completions", json=payload, timeout=DEFAULT_TIMEOUT
    )
    assert response.status_code == 400
