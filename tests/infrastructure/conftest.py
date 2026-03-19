"""
Configuración y fixtures compartidos para tests de infraestructura.

Estos tests verifican que cada contenedor/servicio está corriendo correctamente
y puede realizar operaciones básicas.
"""

import os

import pytest
from dotenv import load_dotenv
from pymongo import MongoClient
from qdrant_client import QdrantClient

# Cargar variables de entorno
load_dotenv()

# =============================================================================
# Constantes de configuración
# =============================================================================

# Timeouts (en segundos)
DEFAULT_TIMEOUT = 5
EMBEDDING_TIMEOUT = 30
LLM_TIMEOUT = 60

# Dimensión de embeddings para nomic-embed-text
NOMIC_EMBED_TEXT_DIMENSION = 768

# URLs de servicios
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
CHATBOT_URL = os.getenv("CHATBOT_URL", "http://localhost:8080")
RAG_SERVICE_URL = os.getenv("RAG_SERVICE_URL", "http://localhost:8081")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
VLLM_URL = os.getenv("VLLM_URL", "http://localhost:8001")

# Configuración de servicios
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))

MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", "27017"))
MONGO_USER = os.getenv("MONGO_ROOT_USERNAME", "root")
MONGO_PASSWORD = os.getenv("MONGO_ROOT_PASSWORD", "example")

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

# Modelo vLLM
VLLM_MODEL_NAME = os.getenv(
    "MODEL_PATH", "/models/unsloth--mistral-7b-instruct-v0.3-bnb-4bit"
)


# =============================================================================
# Fixtures de clientes
# =============================================================================


@pytest.fixture
def mongo_client() -> MongoClient:
    """
    Fixture que proporciona un cliente de MongoDB con cleanup automático.

    Elimina todas las bases de datos de test al finalizar.
    """
    client = MongoClient(
        host=MONGO_HOST,
        port=MONGO_PORT,
        username=MONGO_USER,
        password=MONGO_PASSWORD,
        serverSelectionTimeoutMS=5000,
    )
    yield client

    # Cleanup: eliminar bases de datos de test
    for db_name in client.list_database_names():
        if db_name.startswith("test_"):
            client.drop_database(db_name)
    client.close()


@pytest.fixture
def qdrant_client() -> QdrantClient:
    """
    Fixture que proporciona un cliente de Qdrant con cleanup automático.

    Elimina todas las colecciones de test al finalizar.
    """
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    yield client

    # Cleanup: eliminar colecciones de test
    try:
        collections = client.get_collections()
        for col in collections.collections:
            if col.name.startswith("test_"):
                client.delete_collection(collection_name=col.name)
    except Exception:
        pass  # Ignorar errores de cleanup


# =============================================================================
# Fixtures de URLs
# =============================================================================


@pytest.fixture
def backend_url() -> str:
    """URL del servicio backend."""
    return BACKEND_URL


@pytest.fixture
def chatbot_url() -> str:
    """URL del servicio chatbot."""
    return CHATBOT_URL


@pytest.fixture
def rag_service_url() -> str:
    """URL del servicio RAG."""
    return RAG_SERVICE_URL


@pytest.fixture
def frontend_url() -> str:
    """URL del frontend."""
    return FRONTEND_URL


@pytest.fixture
def ollama_url() -> str:
    """URL del servicio Ollama."""
    return OLLAMA_URL


@pytest.fixture
def qdrant_url() -> str:
    """URL del servicio Qdrant."""
    return QDRANT_URL


@pytest.fixture
def vllm_url() -> str:
    """URL del servicio vLLM."""
    return VLLM_URL
