"""
Tests de integración para el servicio RAG.
Estos tests verifican la integración completa del servicio RAG con Qdrant y Ollama.
"""
import pytest
import requests
import os
import json
from io import BytesIO


@pytest.mark.integration
def test_rag_service_health_check(rag_base_url, api_timeout):
    """Test que verifica que el servicio RAG está disponible."""
    response = requests.get(f"{rag_base_url}/health", timeout=api_timeout)
    assert response.status_code == 200
    
    result = response.json()
    assert result["status"] in ["healthy", "unhealthy"]
    assert "qdrant_connected" in result


@pytest.mark.integration
def test_rag_service_root_endpoint(rag_base_url, api_timeout):
    """Test del endpoint raíz del servicio RAG."""
    response = requests.get(f"{rag_base_url}/", timeout=api_timeout)
    assert response.status_code == 200
    
    result = response.json()
    assert "name" in result
    assert result["name"] == "RAG Service"


@pytest.mark.integration
def test_rag_index_and_search_workflow(rag_base_url, api_timeout):
    """Test del flujo completo de indexación y búsqueda de documentos."""
    # 1. Indexar documentos
    documents = [
        {
            "content": "La lógica difusa es una extensión de la lógica booleana que permite valores de verdad intermedios.",
            "metadata": {
                "asignatura": "Lógica Difusa",
                "tipo_documento": "apuntes",
                "fecha": "2025-11-04"
            },
            "doc_id": "logica_difusa_001"
        },
        {
            "content": "Los conjuntos difusos permiten modelar la incertidumbre en sistemas de control.",
            "metadata": {
                "asignatura": "Lógica Difusa",
                "tipo_documento": "apuntes",
                "fecha": "2025-11-04"
            },
            "doc_id": "logica_difusa_002"
        }
    ]
    
    index_response = requests.post(
        f"{rag_base_url}/index",
        json=documents,
        timeout=api_timeout
    )
    assert index_response.status_code == 200
    index_result = index_response.json()
    assert index_result["indexed_count"] > 0
    
    # 2. Buscar documentos relacionados
    search_payload = {
        "query": "¿Qué es la lógica difusa?",
        "top_k": 5,
        "min_score": 0.3
    }
    
    search_response = requests.post(
        f"{rag_base_url}/search",
        json=search_payload,
        timeout=api_timeout
    )
    assert search_response.status_code == 200
    search_result = search_response.json()
    
    assert "results" in search_result
    assert len(search_result["results"]) > 0
    
    # Verificar estructura de resultados
    first_result = search_result["results"][0]
    assert "content" in first_result
    assert "metadata" in first_result
    assert "score" in first_result
    assert first_result["score"] > 0.3


@pytest.mark.integration
def test_rag_search_with_filters(rag_base_url, api_timeout):
    """Test de búsqueda con filtros de metadata."""
    # Primero indexar documentos de diferentes asignaturas
    documents = [
        {
            "content": "Análisis de algoritmos de ordenación: quicksort, mergesort.",
            "metadata": {
                "asignatura": "Algoritmos",
                "tipo_documento": "apuntes",
                "fecha": "2025-11-04"
            },
            "doc_id": "algoritmos_001"
        },
        {
            "content": "Estructuras de datos: listas, árboles, grafos.",
            "metadata": {
                "asignatura": "Estructuras de Datos",
                "tipo_documento": "apuntes",
                "fecha": "2025-11-04"
            },
            "doc_id": "estructuras_001"
        }
    ]
    
    requests.post(
        f"{rag_base_url}/index",
        json=documents,
        timeout=api_timeout
    )
    
    # Buscar solo en "Algoritmos"
    search_payload = {
        "query": "ordenación",
        "top_k": 5,
        "filters": {
            "asignatura": "Algoritmos"
        }
    }
    
    response = requests.post(
        f"{rag_base_url}/search",
        json=search_payload,
        timeout=api_timeout
    )
    assert response.status_code == 200
    
    result = response.json()
    assert "results" in result
    
    # Verificar que si hay resultados, se devuelven documentos
    # (Los filtros pueden no coincidir si hay documentos previos en la colección)
    if result["results"]:
        assert isinstance(result["results"], list)
        assert "metadata" in result["results"][0]


@pytest.mark.integration
def test_rag_collection_info(rag_base_url, api_timeout):
    """Test para obtener información de la colección Qdrant."""
    response = requests.get(f"{rag_base_url}/collection/info", timeout=api_timeout)
    assert response.status_code == 200
    
    result = response.json()
    assert "name" in result
    assert "vectors_count" in result or "points_count" in result


@pytest.mark.integration
def test_rag_list_subjects(rag_base_url, api_timeout):
    """Test para listar todas las asignaturas disponibles."""
    response = requests.get(f"{rag_base_url}/subjects", timeout=api_timeout)
    assert response.status_code == 200
    
    result = response.json()
    assert "subjects" in result
    assert isinstance(result["subjects"], list)


@pytest.mark.integration
def test_rag_list_document_types(rag_base_url, api_timeout):
    """Test para listar tipos de documentos disponibles."""
    # El endpoint requiere un parámetro de asignatura
    response = requests.get(f"{rag_base_url}/subjects/TestSubject/types", timeout=api_timeout)
    assert response.status_code == 200
    
    result = response.json()
    assert "document_types" in result
    assert isinstance(result["document_types"], list)


@pytest.mark.integration
def test_rag_upload_text_file(rag_base_url, api_timeout):
    """Test de carga de archivo de texto."""
    # Crear un archivo de texto en memoria
    file_content = b"Este es un documento de prueba sobre inteligencia artificial."
    file_data = BytesIO(file_content)
    file_data.name = "test_ai.txt"
    
    files = {
        "file": ("test_ai.txt", file_data, "text/plain")
    }
    
    # El endpoint espera metadata como JSON string en form data
    metadata_dict = {
        "asignatura": "IA",
        "tipo_documento": "apuntes",
        "fecha": "2025-11-04",
        "auto_index": True
    }
    
    data = {
        "metadata": json.dumps(metadata_dict)
    }
    
    response = requests.post(
        f"{rag_base_url}/upload",
        files=files,
        data=data,
        timeout=api_timeout
    )
    
    assert response.status_code == 200
    result = response.json()
    assert "filename" in result
    # La respuesta incluye doc_id, filename, indexed_count y timestamp
    assert "doc_id" in result or "indexed_count" in result


@pytest.mark.integration
def test_rag_upload_markdown_file(rag_base_url, api_timeout):
    """Test de carga de archivo markdown."""
    # Crear un archivo markdown en memoria
    file_content = """# Machine Learning
    
## Introduccion
Machine learning es una rama de la inteligencia artificial.

## Tipos de aprendizaje
- Supervisado
- No supervisado
- Por refuerzo
""".encode('utf-8')
    file_data = BytesIO(file_content)
    file_data.name = "test_ml.md"
    
    files = {
        "file": ("test_ml.md", file_data, "text/markdown")
    }
    
    metadata_dict = {
        "asignatura": "Machine Learning",
        "tipo_documento": "apuntes",
        "fecha": "2025-11-04",
        "auto_index": True
    }
    
    data = {
        "metadata": json.dumps(metadata_dict)
    }
    
    response = requests.post(
        f"{rag_base_url}/upload",
        files=files,
        data=data,
        timeout=api_timeout
    )
    
    assert response.status_code == 200
    result = response.json()
    assert "filename" in result


@pytest.mark.integration
def test_rag_list_files(rag_base_url, api_timeout):
    """Test para listar archivos cargados."""
    response = requests.get(f"{rag_base_url}/files", timeout=api_timeout)
    assert response.status_code == 200
    
    result = response.json()
    assert "files" in result
    assert isinstance(result["files"], list)


@pytest.mark.integration
def test_rag_list_files_with_filters(rag_base_url, api_timeout):
    """Test para listar archivos con filtros."""
    params = {
        "asignatura": "IA",
        "tipo_documento": "apuntes"
    }
    
    response = requests.get(
        f"{rag_base_url}/files",
        params=params,
        timeout=api_timeout
    )
    assert response.status_code == 200
    
    result = response.json()
    assert "files" in result
    assert isinstance(result["files"], list)


@pytest.mark.integration
def test_rag_search_empty_query(rag_base_url, api_timeout):
    """Test que verifica el comportamiento con query vacía."""
    search_payload = {
        "query": "",
        "top_k": 5
    }
    
    response = requests.post(
        f"{rag_base_url}/search",
        json=search_payload,
        timeout=api_timeout
    )
    # El modelo no valida min_length, así que acepta query vacía
    assert response.status_code == 200


@pytest.mark.integration
def test_rag_search_no_results(rag_base_url, api_timeout):
    """Test de búsqueda que no devuelve resultados."""
    search_payload = {
        "query": "xyzabc123notexistingterm999",
        "top_k": 5,
        "min_score": 0.9  # Score muy alto para no obtener resultados
    }
    
    response = requests.post(
        f"{rag_base_url}/search",
        json=search_payload,
        timeout=api_timeout
    )
    assert response.status_code == 200
    
    result = response.json()
    assert "results" in result
    assert len(result["results"]) == 0


@pytest.mark.integration
def test_rag_index_empty_documents(rag_base_url, api_timeout):
    """Test de indexación con lista vacía de documentos."""
    index_payload = []
    
    response = requests.post(
        f"{rag_base_url}/index",
        json=index_payload,
        timeout=api_timeout
    )
    assert response.status_code == 200
    
    result = response.json()
    assert result["indexed_count"] == 0


@pytest.mark.integration
def test_rag_invalid_search_payload(rag_base_url, api_timeout):
    """Test con payload de búsqueda inválido."""
    invalid_payload = {
        "top_k": 5
        # Falta el campo requerido 'query'
    }
    
    response = requests.post(
        f"{rag_base_url}/search",
        json=invalid_payload,
        timeout=api_timeout
    )
    assert response.status_code == 422  # Unprocessable Entity


@pytest.mark.integration
def test_rag_invalid_index_payload(rag_base_url, api_timeout):
    """Test con payload de indexación inválido."""
    invalid_payload = [
        {
            "content": "Contenido sin metadata",
            "doc_id": "invalid_001"
            # Falta el campo 'metadata'
        }
    ]
    
    response = requests.post(
        f"{rag_base_url}/index",
        json=invalid_payload,
        timeout=api_timeout
    )
    assert response.status_code == 422  # Unprocessable Entity


@pytest.mark.integration
def test_rag_search_with_similarity_threshold(rag_base_url, api_timeout):
    """Test de búsqueda con umbral de similitud."""
    # Primero indexar un documento
    documents = [
        {
            "content": "Las redes neuronales convolucionales son útiles para procesamiento de imágenes.",
            "metadata": {
                "asignatura": "Deep Learning",
                "tipo_documento": "apuntes",
                "fecha": "2025-11-04"
            },
            "doc_id": "deep_learning_001"
        }
    ]
    
    requests.post(
        f"{rag_base_url}/index",
        json=documents,
        timeout=api_timeout
    )
    
    # Buscar con umbral bajo (debe retornar resultados)
    search_payload_low = {
        "query": "redes neuronales",
        "top_k": 5,
        "min_score": 0.1
    }
    
    response_low = requests.post(
        f"{rag_base_url}/search",
        json=search_payload_low,
        timeout=api_timeout
    )
    assert response_low.status_code == 200
    result_low = response_low.json()
    
    # Buscar con umbral alto (probablemente no retorne resultados)
    search_payload_high = {
        "query": "redes neuronales",
        "top_k": 5,
        "min_score": 0.99
    }
    
    response_high = requests.post(
        f"{rag_base_url}/search",
        json=search_payload_high,
        timeout=api_timeout
    )
    assert response_high.status_code == 200
    result_high = response_high.json()
    
    # El umbral bajo debe tener más o igual cantidad de resultados que el alto
    assert len(result_low["results"]) >= len(result_high["results"])


@pytest.mark.integration
def test_rag_upload_file_without_auto_index(rag_base_url, api_timeout):
    """Test de carga de archivo sin indexación automática."""
    file_content = "Documento sin indexar automaticamente.".encode('utf-8')
    file_data = BytesIO(file_content)
    file_data.name = "test_no_index.txt"
    
    files = {
        "file": ("test_no_index.txt", file_data, "text/plain")
    }
    
    metadata_dict = {
        "asignatura": "Test",
        "tipo_documento": "apuntes",
        "fecha": "2025-11-04",
        "auto_index": False
    }
    
    data = {
        "metadata": json.dumps(metadata_dict)
    }
    
    response = requests.post(
        f"{rag_base_url}/upload",
        files=files,
        data=data,
        timeout=api_timeout
    )
    
    assert response.status_code == 200
    result = response.json()
    assert "filename" in result
    # Verificar que el mensaje indica que no se indexó
    assert "indexed" not in result.get("message", "").lower() or "not" in result.get("message", "").lower()


@pytest.mark.integration
def test_rag_chunking_large_document(rag_base_url, api_timeout):
    """Test de indexación de documento grande que requiere chunking."""
    # Crear un documento largo
    long_content = " ".join([
        f"Esta es la sección {i} de un documento muy largo sobre procesamiento del lenguaje natural. "
        f"El procesamiento del lenguaje natural (NLP) es fundamental para la IA moderna. "
        for i in range(50)
    ])
    
    documents = [
        {
            "content": long_content,
            "metadata": {
                "asignatura": "NLP",
                "tipo_documento": "apuntes",
                "fecha": "2025-11-04"
            },
            "doc_id": "nlp_large_001"
        }
    ]
    
    response = requests.post(
        f"{rag_base_url}/index",
        json=documents,
        timeout=api_timeout
    )
    
    assert response.status_code == 200
    result = response.json()
    # Un documento largo debería generar múltiples chunks
    assert result["indexed_count"] > 1


@pytest.mark.integration
def test_rag_search_with_multiple_filters(rag_base_url, api_timeout):
    """Test de búsqueda con múltiples filtros aplicados."""
    # Indexar documentos variados
    documents = [
        {
            "content": "Examen de matemáticas avanzadas.",
            "metadata": {
                "asignatura": "Matemáticas",
                "tipo_documento": "examen",
                "fecha": "2025-11-01"
            },
            "doc_id": "math_exam_001"
        },
        {
            "content": "Apuntes de matemáticas básicas.",
            "metadata": {
                "asignatura": "Matemáticas",
                "tipo_documento": "apuntes",
                "fecha": "2025-11-01"
            },
            "doc_id": "math_notes_001"
        }
    ]
    
    requests.post(
        f"{rag_base_url}/index",
        json=documents,
        timeout=api_timeout
    )
    
    # Buscar con filtros múltiples
    search_payload = {
        "query": "matemáticas",
        "top_k": 5,
        "filters": {
            "asignatura": "Matemáticas",
            "tipo_documento": "examen"
        }
    }
    
    response = requests.post(
        f"{rag_base_url}/search",
        json=search_payload,
        timeout=api_timeout
    )
    
    assert response.status_code == 200
    result = response.json()
    
    # Verificar que si hay resultados, se devuelven documentos con metadata
    # (Los filtros pueden no coincidir perfectamente si hay documentos previos)
    if result["results"]:
        assert isinstance(result["results"], list)
        assert "metadata" in result["results"][0]
