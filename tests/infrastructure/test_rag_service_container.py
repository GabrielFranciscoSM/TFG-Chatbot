"""
Tests para verificar el funcionamiento del contenedor del servicio RAG.
Estos tests verifican que el contenedor está corriendo y responde correctamente.
"""
import pytest
import requests


RAG_SERVICE_URL = "http://localhost:8081"


def test_rag_service_container_is_running():
    """Verifica que el contenedor del servicio RAG está corriendo y responde."""
    try:
        resp = requests.get(f"{RAG_SERVICE_URL}/health", timeout=5)
        assert resp.status_code == 200
        data = resp.json()
        assert "status" in data
        assert data["status"] in ["healthy", "unhealthy"]
    except requests.exceptions.ConnectionError:
        pytest.fail("El contenedor del servicio RAG no está disponible en http://localhost:8081")


def test_rag_service_container_root_endpoint():
    """Verifica que el endpoint raíz del servicio RAG funciona correctamente."""
    resp = requests.get(f"{RAG_SERVICE_URL}/", timeout=5)
    assert resp.status_code == 200
    data = resp.json()
    assert "name" in data
    assert data["name"] == "RAG Service"
    assert "version" in data


def test_rag_service_accepts_search_requests():
    """Verifica que el servicio RAG acepta peticiones de búsqueda."""
    payload = {
        "query": "test query",
        "top_k": 5,
        "min_score": 0.3
    }
    resp = requests.post(f"{RAG_SERVICE_URL}/search", json=payload, timeout=10)
    assert resp.status_code == 200
    data = resp.json()
    
    # Verificar estructura de la respuesta
    assert "results" in data
    assert isinstance(data["results"], list)


def test_rag_service_accepts_index_requests():
    """Verifica que el servicio RAG acepta peticiones de indexación."""
    payload = [
        {
            "content": "Test document for infrastructure testing",
            "metadata": {
                "asignatura": "Test",
                "tipo_documento": "apuntes",
                "fecha": "2025-11-04"
            },
            "doc_id": "infra_test_001"
        }
    ]
    resp = requests.post(f"{RAG_SERVICE_URL}/index", json=payload, timeout=30)
    assert resp.status_code == 200
    data = resp.json()
    
    # Verificar estructura de la respuesta
    assert "indexed_count" in data
    assert isinstance(data["indexed_count"], int)
    assert data["indexed_count"] >= 0


def test_rag_service_validates_search_payload():
    """Verifica que el servicio RAG valida correctamente los payloads de búsqueda."""
    # Payload sin campo 'query' requerido
    invalid_payload = {
        "top_k": 5
    }
    resp = requests.post(f"{RAG_SERVICE_URL}/search", json=invalid_payload, timeout=5)
    assert resp.status_code == 422  # Unprocessable Entity


def test_rag_service_validates_index_payload():
    """Verifica que el servicio RAG valida correctamente los payloads de indexación."""
    # Payload sin campo 'documents' requerido
    invalid_payload = {}
    resp = requests.post(f"{RAG_SERVICE_URL}/index", json=invalid_payload, timeout=5)
    assert resp.status_code == 422  # Unprocessable Entity


def test_rag_service_collection_info():
    """Verifica que el servicio RAG puede obtener información de la colección."""
    resp = requests.get(f"{RAG_SERVICE_URL}/collection/info", timeout=5)
    assert resp.status_code == 200
    data = resp.json()
    
    # Verificar estructura de la respuesta
    assert "name" in data
    assert isinstance(data["name"], str)


def test_rag_service_list_subjects():
    """Verifica que el servicio RAG puede listar asignaturas."""
    resp = requests.get(f"{RAG_SERVICE_URL}/subjects", timeout=5)
    assert resp.status_code == 200
    data = resp.json()
    
    # Verificar estructura de la respuesta
    assert "subjects" in data
    assert isinstance(data["subjects"], list)


def test_rag_service_list_document_types():
    """Verifica que el servicio RAG puede listar tipos de documentos."""
    # El endpoint requiere un parámetro de asignatura
    resp = requests.get(f"{RAG_SERVICE_URL}/subjects/TestSubject/types", timeout=5)
    assert resp.status_code == 200
    data = resp.json()
    
    # Verificar estructura de la respuesta
    assert "document_types" in data
    assert isinstance(data["document_types"], list)


def test_rag_service_list_files():
    """Verifica que el servicio RAG puede listar archivos."""
    resp = requests.get(f"{RAG_SERVICE_URL}/files", timeout=5)
    assert resp.status_code == 200
    data = resp.json()
    
    # Verificar estructura de la respuesta
    assert "files" in data
    assert isinstance(data["files"], list)
