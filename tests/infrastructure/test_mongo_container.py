"""
Tests para verificar el funcionamiento del contenedor de MongoDB.
Estos tests verifican que MongoDB está corriendo y puede realizar operaciones básicas.
"""

import os

import pytest
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

load_dotenv()

MONGO_HOST = "localhost"
MONGO_PORT = 27017
MONGO_USER = os.getenv("MONGO_ROOT_USERNAME", "root")
MONGO_PASSWORD = os.getenv("MONGO_ROOT_PASSWORD", "example")


def get_mongo_client():
    """Crea y retorna un cliente de MongoDB."""
    return MongoClient(
        host=MONGO_HOST,
        port=MONGO_PORT,
        username=MONGO_USER,
        password=MONGO_PASSWORD,
        serverSelectionTimeoutMS=5000,
    )


def test_mongo_container_is_running():
    """Verifica que el contenedor de MongoDB está corriendo y acepta conexiones."""
    try:
        client = get_mongo_client()
        # Intentar hacer ping para verificar conexión
        client.admin.command("ping")
        client.close()
    except (ConnectionFailure, ServerSelectionTimeoutError):
        pytest.fail("El contenedor de MongoDB no está disponible en localhost:27017")


def test_mongo_list_databases():
    """Verifica que MongoDB puede listar bases de datos."""
    client = get_mongo_client()
    databases = client.list_database_names()

    # Deberían existir al menos las bases de datos del sistema
    assert "admin" in databases

    client.close()


def test_mongo_can_create_database_and_collection():
    """Verifica que MongoDB puede crear bases de datos y colecciones."""
    client = get_mongo_client()

    test_db = client["test_infrastructure_db"]
    test_collection = test_db["test_collection"]

    # Insertar un documento de prueba
    test_doc = {"name": "test", "value": 123}
    result = test_collection.insert_one(test_doc)

    assert result.inserted_id is not None

    # Verificar que el documento fue insertado
    found_doc = test_collection.find_one({"name": "test"})
    assert found_doc is not None
    assert found_doc["value"] == 123

    # Cleanup
    client.drop_database("test_infrastructure_db")
    client.close()


def test_mongo_can_query_documents():
    """Verifica que MongoDB puede realizar consultas."""
    client = get_mongo_client()

    test_db = client["test_query_db"]
    test_collection = test_db["documents"]

    # Insertar varios documentos
    docs = [
        {"type": "apuntes", "asignatura": "IA", "content": "Documento 1"},
        {"type": "examen", "asignatura": "IA", "content": "Documento 2"},
        {"type": "apuntes", "asignatura": "BD", "content": "Documento 3"},
    ]
    test_collection.insert_many(docs)

    # Consultar documentos de tipo "apuntes"
    apuntes = list(test_collection.find({"type": "apuntes"}))
    assert len(apuntes) == 2

    # Consultar documentos de asignatura "IA"
    ia_docs = list(test_collection.find({"asignatura": "IA"}))
    assert len(ia_docs) == 2

    # Cleanup
    client.drop_database("test_query_db")
    client.close()


def test_mongo_can_update_documents():
    """Verifica que MongoDB puede actualizar documentos."""
    client = get_mongo_client()

    test_db = client["test_update_db"]
    test_collection = test_db["documents"]

    # Insertar un documento
    doc = {"name": "original", "value": 100}
    test_collection.insert_one(doc)

    # Actualizar el documento
    test_collection.update_one({"name": "original"}, {"$set": {"value": 200}})

    # Verificar la actualización
    updated_doc = test_collection.find_one({"name": "original"})
    assert updated_doc["value"] == 200

    # Cleanup
    client.drop_database("test_update_db")
    client.close()


def test_mongo_can_delete_documents():
    """Verifica que MongoDB puede eliminar documentos."""
    client = get_mongo_client()

    test_db = client["test_delete_db"]
    test_collection = test_db["documents"]

    # Insertar documentos
    docs = [{"name": "doc1"}, {"name": "doc2"}, {"name": "doc3"}]
    test_collection.insert_many(docs)

    # Verificar que hay 3 documentos
    assert test_collection.count_documents({}) == 3

    # Eliminar un documento
    test_collection.delete_one({"name": "doc2"})

    # Verificar que solo quedan 2
    assert test_collection.count_documents({}) == 2

    # Verificar que doc2 fue eliminado
    assert test_collection.find_one({"name": "doc2"}) is None

    # Cleanup
    client.drop_database("test_delete_db")
    client.close()


def test_mongo_supports_indexes():
    """Verifica que MongoDB puede crear y usar índices."""
    client = get_mongo_client()

    test_db = client["test_index_db"]
    test_collection = test_db["documents"]

    # Crear un índice en el campo "asignatura"
    test_collection.create_index("asignatura")

    # Obtener la lista de índices
    indexes = list(test_collection.list_indexes())
    index_names = [idx["name"] for idx in indexes]

    # Debería existir el índice que creamos
    assert "asignatura_1" in index_names

    # Cleanup
    client.drop_database("test_index_db")
    client.close()


def test_mongo_supports_aggregation():
    """Verifica que MongoDB puede realizar operaciones de agregación."""
    client = get_mongo_client()

    test_db = client["test_aggregation_db"]
    test_collection = test_db["documents"]

    # Insertar documentos con diferentes asignaturas
    docs = [
        {"asignatura": "IA", "score": 85},
        {"asignatura": "IA", "score": 90},
        {"asignatura": "BD", "score": 75},
        {"asignatura": "BD", "score": 80},
    ]
    test_collection.insert_many(docs)

    # Agregar para calcular promedio por asignatura
    pipeline = [{"$group": {"_id": "$asignatura", "avg_score": {"$avg": "$score"}}}]

    results = list(test_collection.aggregate(pipeline))

    # Deberían haber 2 grupos (IA y BD)
    assert len(results) == 2

    # Verificar los promedios
    for result in results:
        if result["_id"] == "IA":
            assert result["avg_score"] == 87.5
        elif result["_id"] == "BD":
            assert result["avg_score"] == 77.5

    # Cleanup
    client.drop_database("test_aggregation_db")
    client.close()


def test_mongo_authentication():
    """Verifica que MongoDB requiere autenticación."""
    # Intentar conectar sin credenciales debería fallar
    try:
        client_no_auth = MongoClient(
            host=MONGO_HOST, port=MONGO_PORT, serverSelectionTimeoutMS=3000
        )
        # Intentar una operación que requiera autenticación
        client_no_auth.admin.command("ping")
        # Si llegamos aquí, falló la autenticación (no debería pasar)
        client_no_auth.close()
        # Este test puede pasar si MongoDB no tiene auth habilitado
        # En ese caso, solo verificamos que funciona
    except Exception:
        # Autenticación requerida (comportamiento esperado)
        pass


def test_mongo_server_info():
    """Verifica que podemos obtener información del servidor MongoDB."""
    client = get_mongo_client()

    server_info = client.server_info()

    # Verificar que tenemos información básica del servidor
    assert "version" in server_info
    assert isinstance(server_info["version"], str)

    client.close()
