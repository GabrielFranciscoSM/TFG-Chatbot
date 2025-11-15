"""
Configuración específica para tests de integración.
"""

import os
import time

import pytest
import requests


@pytest.fixture(scope="session", autouse=True)
def verify_api_available(api_base_url):
    """
    Fixture que verifica que la API está disponible antes de ejecutar los tests.
    Se ejecuta automáticamente al inicio de la sesión de tests.
    """
    max_retries = 30
    retry_delay = 2  # segundos

    print(f"\nVerificando disponibilidad de la API en {api_base_url}...")

    for attempt in range(max_retries):
        try:
            response = requests.get(f"{api_base_url}/health", timeout=5)
            if response.status_code == 200:
                print(f"✓ API disponible en {api_base_url}")
                return
        except (requests.ConnectionError, requests.Timeout):
            if attempt < max_retries - 1:
                print(
                    f"Intento {attempt + 1}/{max_retries} - API no disponible, reintentando en {retry_delay}s..."
                )
                time.sleep(retry_delay)
            else:
                raise

    pytest.fail(
        f"La API no está disponible en {api_base_url} después de {max_retries} intentos. "
        "Asegúrate de que los contenedores estén corriendo con 'docker-compose up -d'"
    )


@pytest.fixture(scope="session")
def verify_rag_service_available(rag_base_url):
    """
    Fixture que verifica que el servicio RAG está disponible antes de ejecutar los tests.
    Se ejecuta automáticamente al inicio de la sesión de tests.
    """
    max_retries = 30
    retry_delay = 2  # segundos

    print(f"\nVerificando disponibilidad del servicio RAG en {rag_base_url}...")

    for attempt in range(max_retries):
        try:
            response = requests.get(f"{rag_base_url}/health", timeout=5)
            if response.status_code == 200:
                print(f"✓ Servicio RAG disponible en {rag_base_url}")
                return
        except (requests.ConnectionError, requests.Timeout):
            if attempt < max_retries - 1:
                print(
                    f"Intento {attempt + 1}/{max_retries} - Servicio RAG no disponible, reintentando en {retry_delay}s..."
                )
                time.sleep(retry_delay)
            else:
                raise

    pytest.fail(
        f"El servicio RAG no está disponible en {rag_base_url} después de {max_retries} intentos. "
        "Asegúrate de que los contenedores estén corriendo con 'docker-compose up -d'"
    )


@pytest.fixture(scope="session")
def api_timeout():
    """
    Timeout para las peticiones HTTP a la API.
    Puede configurarse con la variable de entorno API_TIMEOUT.
    """
    return int(os.getenv("API_TIMEOUT", "30"))
