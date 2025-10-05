import pytest
import requests
import testinfra
import os
from dotenv import load_dotenv

load_dotenv()
API_URL = "http://localhost:" + os.getenv("VLLM_MAIN_PORT","8000")
MAIN_VLLM_MODEL_NAME = os.getenv("MODEL_PATH","/models/unsloth--mistral-7b-instruct-v0.3-bnb-4bit") 


def test_health_endpoint():
    resp = requests.get(f"{API_URL}/health")
    assert resp.status_code == 200


def test_chat_completions():
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
    payload = {
        "model": "modelo-inexistente",
        "messages": [{"role": "user", "content": "Hola"}],
        "max_tokens": 10
    }
    response = requests.post(f"{API_URL}/v1/chat/completions", json=payload)
    assert response.status_code == 400 or response.status_code == 404

def test_invalid_message_format():
    payload = {
        "model": "tu-modelo",
        "messages": [{"content": "Hola"}],  # Falta 'role'
        "max_tokens": 10
    }
    response = requests.post(f"{API_URL}/v1/chat/completions", json=payload)
    assert response.status_code == 400

def test_invalid_tool_definition():
    payload = {
        "model": "tu-modelo",
        "messages": [{"role": "user", "content": "¿Qué tiempo hace?"}],
        "tools": [{"type": "function"}],  # Falta 'function' details
        "max_tokens": 10
    }
    response = requests.post(f"{API_URL}/v1/chat/completions", json=payload)
    assert response.status_code == 400