"""
Tests para verificar el funcionamiento del contenedor de Qdrant.
Estos tests verifican que Qdrant está corriendo y puede realizar operaciones básicas.
"""
import pytest
import requests
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct


QDRANT_URL = "http://localhost:6333"


def test_qdrant_container_is_running():
    """Verifica que el contenedor de Qdrant está corriendo y responde."""
    try:
        resp = requests.get(f"{QDRANT_URL}/", timeout=5)
        assert resp.status_code == 200
        data = resp.json()
        assert "title" in data
        assert data["title"] == "qdrant - vector search engine"
    except requests.exceptions.ConnectionError:
        pytest.fail("El contenedor de Qdrant no está disponible en http://localhost:6333")


def test_qdrant_health_endpoint():
    """Verifica que el endpoint de health de Qdrant responde correctamente."""
    resp = requests.get(f"{QDRANT_URL}/healthz", timeout=5)
    assert resp.status_code == 200


def test_qdrant_can_create_collection():
    """Verifica que Qdrant puede crear colecciones."""
    client = QdrantClient(host="localhost", port=6333)
    
    collection_name = "test_infrastructure_collection"
    
    # Eliminar la colección si ya existe (cleanup)
    try:
        client.delete_collection(collection_name=collection_name)
    except Exception:
        pass  # La colección no existe, continuar
    
    # Crear una nueva colección
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=128, distance=Distance.COSINE)
    )
    
    # Verificar que la colección fue creada
    collections = client.get_collections()
    collection_names = [col.name for col in collections.collections]
    assert collection_name in collection_names
    
    # Cleanup
    client.delete_collection(collection_name=collection_name)


def test_qdrant_can_insert_and_search_vectors():
    """Verifica que Qdrant puede insertar y buscar vectores."""
    client = QdrantClient(host="localhost", port=6333)
    
    collection_name = "test_search_collection"
    
    # Eliminar la colección si ya existe
    try:
        client.delete_collection(collection_name=collection_name)
    except Exception:
        pass
    
    # Crear colección
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=128, distance=Distance.COSINE)
    )
    
    # Insertar algunos puntos
    points = [
        PointStruct(
            id=1,
            vector=[0.1] * 128,
            payload={"text": "documento 1", "asignatura": "IA"}
        ),
        PointStruct(
            id=2,
            vector=[0.2] * 128,
            payload={"text": "documento 2", "asignatura": "BD"}
        )
    ]
    
    client.upsert(collection_name=collection_name, points=points)
    
    # Realizar una búsqueda
    search_result = client.query_points(
        collection_name=collection_name,
        query=[0.15] * 128,
        limit=2
    )
    
    assert len(search_result.points) > 0
    assert search_result.points[0].payload is not None
    
    # Cleanup
    client.delete_collection(collection_name=collection_name)


def test_qdrant_can_filter_by_metadata():
    """Verifica que Qdrant puede filtrar resultados por metadata."""
    client = QdrantClient(host="localhost", port=6333)
    
    collection_name = "test_filter_collection"
    
    # Eliminar la colección si ya existe
    try:
        client.delete_collection(collection_name=collection_name)
    except Exception:
        pass
    
    # Crear colección
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=128, distance=Distance.COSINE)
    )
    
    # Insertar puntos con diferentes metadata
    points = [
        PointStruct(
            id=1,
            vector=[0.1] * 128,
            payload={"text": "apuntes IA", "asignatura": "IA", "tipo": "apuntes"}
        ),
        PointStruct(
            id=2,
            vector=[0.1] * 128,
            payload={"text": "examen IA", "asignatura": "IA", "tipo": "examen"}
        ),
        PointStruct(
            id=3,
            vector=[0.1] * 128,
            payload={"text": "apuntes BD", "asignatura": "BD", "tipo": "apuntes"}
        )
    ]
    
    client.upsert(collection_name=collection_name, points=points)
    
    # Buscar solo documentos de tipo "apuntes"
    from qdrant_client.models import Filter, FieldCondition, MatchValue
    
    search_result = client.query_points(
        collection_name=collection_name,
        query=[0.1] * 128,
        query_filter=Filter(
            must=[
                FieldCondition(
                    key="tipo",
                    match=MatchValue(value="apuntes")
                )
            ]
        ),
        limit=10
    )
    
    # Verificar que solo devuelve documentos de tipo "apuntes"
    assert len(search_result.points) == 2
    for result in search_result.points:
        assert result.payload["tipo"] == "apuntes"
    
    # Cleanup
    client.delete_collection(collection_name=collection_name)


def test_qdrant_collection_info():
    """Verifica que Qdrant puede proporcionar información de una colección."""
    client = QdrantClient(host="localhost", port=6333)
    
    collection_name = "test_info_collection"
    
    # Eliminar la colección si ya existe
    try:
        client.delete_collection(collection_name=collection_name)
    except Exception:
        pass
    
    # Crear colección
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=128, distance=Distance.COSINE)
    )
    
    # Obtener información de la colección
    collection_info = client.get_collection(collection_name=collection_name)
    
    assert collection_info.status == "green"
    # vectors_count puede ser None en algunas versiones de Qdrant
    assert collection_info.points_count == 0  # Recién creada, sin puntos
    
    # Cleanup
    client.delete_collection(collection_name=collection_name)


def test_qdrant_list_collections():
    """Verifica que Qdrant puede listar todas las colecciones."""
    client = QdrantClient(host="localhost", port=6333)
    
    # Obtener lista de colecciones
    collections = client.get_collections()
    
    assert hasattr(collections, 'collections')
    assert isinstance(collections.collections, list)


def test_qdrant_rest_api_collections():
    """Verifica que la REST API de Qdrant funciona correctamente."""
    resp = requests.get(f"{QDRANT_URL}/collections", timeout=5)
    assert resp.status_code == 200
    
    data = resp.json()
    assert "result" in data
    assert "collections" in data["result"]
    assert isinstance(data["result"]["collections"], list)
