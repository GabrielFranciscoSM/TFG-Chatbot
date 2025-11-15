"""
Tests para verificar el funcionamiento del contenedor de Ollama.
Estos tests verifican que Ollama está corriendo y puede generar embeddings.
"""

import pytest
import requests

OLLAMA_URL = "http://localhost:11435"
EMBEDDING_MODEL = "nomic-embed-text"


def test_ollama_container_is_running():
    """Verifica que el contenedor de Ollama está corriendo y responde."""
    try:
        resp = requests.get(f"{OLLAMA_URL}/", timeout=5)
        assert resp.status_code == 200
        assert resp.text == "Ollama is running"
    except requests.exceptions.ConnectionError:
        pytest.fail(
            "El contenedor de Ollama no está disponible en http://localhost:11435"
        )


def test_ollama_api_version():
    """Verifica que el endpoint de versión de Ollama responde."""
    resp = requests.get(f"{OLLAMA_URL}/api/version", timeout=5)
    assert resp.status_code == 200
    data = resp.json()
    assert "version" in data


def test_ollama_list_models():
    """Verifica que Ollama puede listar los modelos instalados."""
    resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
    assert resp.status_code == 200
    data = resp.json()
    assert "models" in data
    assert isinstance(data["models"], list)


def test_ollama_embedding_model_available():
    """Verifica que el modelo de embeddings está disponible."""
    resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
    assert resp.status_code == 200
    data = resp.json()

    model_names = [model["name"] for model in data["models"]]
    # El modelo puede tener :latest al final
    assert any(
        EMBEDDING_MODEL in name for name in model_names
    ), f"Modelo {EMBEDDING_MODEL} no encontrado. Modelos disponibles: {model_names}"


def test_ollama_can_generate_embeddings():
    """Verifica que Ollama puede generar embeddings."""
    payload = {
        "model": EMBEDDING_MODEL,
        "prompt": "This is a test document for embedding generation",
    }

    resp = requests.post(f"{OLLAMA_URL}/api/embeddings", json=payload, timeout=30)
    assert resp.status_code == 200
    data = resp.json()

    # Verificar estructura de la respuesta
    assert "embedding" in data
    assert isinstance(data["embedding"], list)
    assert len(data["embedding"]) > 0

    # Verificar que los valores son números
    assert all(isinstance(x, (int, float)) for x in data["embedding"])


def test_ollama_embeddings_dimension():
    """Verifica que los embeddings tienen la dimensión correcta (768 para nomic-embed-text)."""
    payload = {"model": EMBEDDING_MODEL, "prompt": "Test text"}

    resp = requests.post(f"{OLLAMA_URL}/api/embeddings", json=payload, timeout=30)
    assert resp.status_code == 200
    data = resp.json()

    # nomic-embed-text genera embeddings de 768 dimensiones
    assert len(data["embedding"]) == 768


def test_ollama_embeddings_consistency():
    """Verifica que Ollama genera embeddings consistentes para el mismo texto."""
    payload = {"model": EMBEDDING_MODEL, "prompt": "Consistent test text"}

    # Generar primer embedding
    resp1 = requests.post(f"{OLLAMA_URL}/api/embeddings", json=payload, timeout=30)
    assert resp1.status_code == 200
    embedding1 = resp1.json()["embedding"]

    # Generar segundo embedding con el mismo texto
    resp2 = requests.post(f"{OLLAMA_URL}/api/embeddings", json=payload, timeout=30)
    assert resp2.status_code == 200
    embedding2 = resp2.json()["embedding"]

    # Los embeddings deberían ser idénticos (o muy similares)
    assert len(embedding1) == len(embedding2)
    # Verificar que son muy similares (pueden tener pequeñas diferencias por floating point)
    differences = sum(abs(a - b) for a, b in zip(embedding1, embedding2, strict=True))
    assert differences < 0.01  # Tolerancia muy pequeña


def test_ollama_multiple_embeddings():
    """Verifica que Ollama puede generar múltiples embeddings en secuencia."""
    texts = ["First test document", "Second test document", "Third test document"]

    embeddings = []
    for text in texts:
        payload = {"model": EMBEDDING_MODEL, "prompt": text}
        resp = requests.post(f"{OLLAMA_URL}/api/embeddings", json=payload, timeout=30)
        assert resp.status_code == 200
        embeddings.append(resp.json()["embedding"])

    # Verificar que todos tienen la misma dimensión
    assert len(embeddings) == 3
    assert all(len(emb) == 768 for emb in embeddings)

    # Verificar que son diferentes (no idénticos)
    assert embeddings[0] != embeddings[1]
    assert embeddings[1] != embeddings[2]


def test_ollama_empty_text_handling():
    """Verifica cómo Ollama maneja textos vacíos."""
    payload = {"model": EMBEDDING_MODEL, "prompt": ""}

    resp = requests.post(f"{OLLAMA_URL}/api/embeddings", json=payload, timeout=30)
    # Debería responder correctamente incluso con texto vacío
    assert resp.status_code == 200
    data = resp.json()
    assert "embedding" in data
    # Ollama retorna un array vacío para texto vacío
    assert isinstance(data["embedding"], list)


def test_ollama_long_text_handling():
    """Verifica que Ollama puede manejar textos largos."""
    long_text = " ".join(["Test word"] * 1000)  # Texto muy largo

    payload = {"model": EMBEDDING_MODEL, "prompt": long_text}

    resp = requests.post(f"{OLLAMA_URL}/api/embeddings", json=payload, timeout=60)
    assert resp.status_code == 200
    data = resp.json()
    assert "embedding" in data
    assert len(data["embedding"]) == 768


def test_ollama_invalid_model():
    """Verifica que Ollama maneja correctamente peticiones con modelos inválidos."""
    payload = {"model": "modelo-que-no-existe", "prompt": "Test text"}

    resp = requests.post(f"{OLLAMA_URL}/api/embeddings", json=payload, timeout=10)
    # Debería devolver error
    assert resp.status_code != 200


def test_ollama_special_characters():
    """Verifica que Ollama puede manejar caracteres especiales y acentos."""
    payload = {
        "model": EMBEDDING_MODEL,
        "prompt": "Texto con áéíóú ñ y símbolos: @#$%&*()[]{}|\\<>?/",
    }

    resp = requests.post(f"{OLLAMA_URL}/api/embeddings", json=payload, timeout=30)
    assert resp.status_code == 200
    data = resp.json()
    assert "embedding" in data
    assert len(data["embedding"]) == 768
