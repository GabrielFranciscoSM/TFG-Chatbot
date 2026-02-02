"""
Tests para verificar el funcionamiento del contenedor de Qdrant.
Estos tests verifican que Qdrant está corriendo y puede realizar operaciones básicas.
"""

import pytest
import requests
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from tests.infrastructure.conftest import DEFAULT_TIMEOUT, QDRANT_URL

# Aplicar marker a todos los tests de este módulo
pytestmark = pytest.mark.podman_container

# Dimensión de vectores para tests
TEST_VECTOR_SIZE = 128


def test_qdrant_container_is_running():
    """Verifica que el contenedor de Qdrant está corriendo y responde."""
    try:
        resp = requests.get(f"{QDRANT_URL}/", timeout=DEFAULT_TIMEOUT)
        assert resp.status_code == 200
        data = resp.json()
        assert "title" in data
        assert data["title"] == "qdrant - vector search engine"
    except requests.exceptions.ConnectionError:
        pytest.fail(f"El contenedor de Qdrant no está disponible en {QDRANT_URL}")


def test_qdrant_health_endpoint():
    """Verifica que el endpoint de health de Qdrant responde correctamente."""
    resp = requests.get(f"{QDRANT_URL}/healthz", timeout=DEFAULT_TIMEOUT)
    assert resp.status_code == 200


def test_qdrant_can_create_collection(qdrant_client):
    """Verifica que Qdrant puede crear colecciones."""
    collection_name = "test_infrastructure_collection"

    # Eliminar la colección si ya existe (cleanup)
    try:
        qdrant_client.delete_collection(collection_name=collection_name)
    except UnexpectedResponse:
        pass  # La colección no existe

    # Crear una nueva colección
    qdrant_client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=TEST_VECTOR_SIZE, distance=Distance.COSINE),
    )

    # Verificar que la colección fue creada
    collections = qdrant_client.get_collections()
    collection_names = [col.name for col in collections.collections]
    assert collection_name in collection_names


def test_qdrant_can_insert_and_search_vectors(qdrant_client):
    """Verifica que Qdrant puede insertar y buscar vectores."""
    collection_name = "test_search_collection"

    # Eliminar la colección si ya existe
    try:
        qdrant_client.delete_collection(collection_name=collection_name)
    except UnexpectedResponse:
        pass

    # Crear colección
    qdrant_client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=TEST_VECTOR_SIZE, distance=Distance.COSINE),
    )

    # Insertar algunos puntos
    points = [
        PointStruct(
            id=1,
            vector=[0.1] * TEST_VECTOR_SIZE,
            payload={"text": "documento 1", "asignatura": "IA"},
        ),
        PointStruct(
            id=2,
            vector=[0.2] * TEST_VECTOR_SIZE,
            payload={"text": "documento 2", "asignatura": "BD"},
        ),
    ]

    qdrant_client.upsert(collection_name=collection_name, points=points)

    # Realizar una búsqueda
    search_result = qdrant_client.query_points(
        collection_name=collection_name, query=[0.15] * TEST_VECTOR_SIZE, limit=2
    )

    assert len(search_result.points) > 0
    assert search_result.points[0].payload is not None


def test_qdrant_can_filter_by_metadata(qdrant_client):
    """Verifica que Qdrant puede filtrar resultados por metadata."""
    collection_name = "test_filter_collection"

    # Eliminar la colección si ya existe
    try:
        qdrant_client.delete_collection(collection_name=collection_name)
    except UnexpectedResponse:
        pass

    # Crear colección
    qdrant_client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=TEST_VECTOR_SIZE, distance=Distance.COSINE),
    )

    # Insertar puntos con diferentes metadata
    points = [
        PointStruct(
            id=1,
            vector=[0.1] * TEST_VECTOR_SIZE,
            payload={"text": "apuntes IA", "asignatura": "IA", "tipo": "apuntes"},
        ),
        PointStruct(
            id=2,
            vector=[0.1] * TEST_VECTOR_SIZE,
            payload={"text": "examen IA", "asignatura": "IA", "tipo": "examen"},
        ),
        PointStruct(
            id=3,
            vector=[0.1] * TEST_VECTOR_SIZE,
            payload={"text": "apuntes BD", "asignatura": "BD", "tipo": "apuntes"},
        ),
    ]

    qdrant_client.upsert(collection_name=collection_name, points=points)

    # Buscar solo documentos de tipo "apuntes"
    search_result = qdrant_client.query_points(
        collection_name=collection_name,
        query=[0.1] * TEST_VECTOR_SIZE,
        query_filter=Filter(
            must=[FieldCondition(key="tipo", match=MatchValue(value="apuntes"))]
        ),
        limit=10,
    )

    # Verificar que solo devuelve documentos de tipo "apuntes"
    assert len(search_result.points) == 2
    for result in search_result.points:
        assert result.payload["tipo"] == "apuntes"


def test_qdrant_collection_info(qdrant_client):
    """Verifica que Qdrant puede proporcionar información de una colección."""
    collection_name = "test_info_collection"

    # Eliminar la colección si ya existe
    try:
        qdrant_client.delete_collection(collection_name=collection_name)
    except UnexpectedResponse:
        pass

    # Crear colección
    qdrant_client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=TEST_VECTOR_SIZE, distance=Distance.COSINE),
    )

    # Obtener información de la colección
    collection_info = qdrant_client.get_collection(collection_name=collection_name)

    assert collection_info.status == "green"
    assert collection_info.points_count == 0  # Recién creada, sin puntos


def test_qdrant_list_collections(qdrant_client):
    """Verifica que Qdrant puede listar todas las colecciones."""
    collections = qdrant_client.get_collections()

    assert hasattr(collections, "collections")
    assert isinstance(collections.collections, list)


def test_qdrant_rest_api_collections():
    """Verifica que la REST API de Qdrant funciona correctamente."""
    resp = requests.get(f"{QDRANT_URL}/collections", timeout=DEFAULT_TIMEOUT)
    assert resp.status_code == 200

    data = resp.json()
    assert "result" in data
    assert "collections" in data["result"]
    assert isinstance(data["result"]["collections"], list)
