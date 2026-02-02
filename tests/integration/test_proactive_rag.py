import uuid

import pytest
import requests


@pytest.mark.integration
def test_proactive_rag_test_generation(
    api_base_url, session_id, api_timeout, auth_token
):
    """
    Test que verifica el flujo proactivo de RAG durante la generación de un test.
    """
    headers = {"Authorization": f"Bearer {auth_token}"}

    # 1. Solicitar un test sobre un tema específico
    # Usamos un tema que genere consultas de búsqueda
    payload = {
        "query": "Hazme un test corto sobre Docker y contenedores",
        "id": session_id,
        "asignatura": "iv",
    }

    response = requests.post(
        f"{api_base_url}/chat", json=payload, headers=headers, timeout=api_timeout
    )

    assert response.status_code == 200
    result = response.json()

    # El primer mensaje debe ser la confirmación de preparación (ToolMessage content en el grafo)
    # o directamente la primera pregunta si el flujo es rápido.
    # En la implementación actual, initialize_test devuelve un ToolMessage "Preparando..."
    # Pero el grafo sigue ejecutando hasta llegar a un interrupt.

    assert "message" in result
    content = result["message"]["content"]

    # Verificamos que el flujo se haya iniciado correctamente
    # Debería mostrar un mensaje indicando que recopiló información (de generate_questions_node)
    # y luego la primera pregunta (de present_question).
    assert "información relevante" in content.lower() or "pregunta" in content.lower()

    # 2. Verificar que el estado del test se ha inicializado
    # Podríamos consultar el estado si hubiera un endpoint para ello,
    # pero aquí confiamos en la respuesta del chat.

    # 3. Responder a la primera pregunta para ver si el flujo continúa
    # Extraemos el texto de la pregunta para el log
    print(f"Pregunta recibida: {content[:100]}...")

    resume_payload = {
        "user_response": "Es una herramienta de virtualización a nivel de SO",
        "id": session_id,
    }

    response_2 = requests.post(
        f"{api_base_url}/resume_chat",
        json=resume_payload,
        headers=headers,
        timeout=api_timeout,
    )

    assert response_2.status_code == 200
    result_2 = response_2.json()
    assert "message" in result_2
    # If it's the second question, it should ideally have feedback from the first one
    # Note: Sometimes the LLM might be slow or the feedback might be subtle.
    # We check if it contains the "Resultados" prefix we added in testGraph.py
    assert (
        "resultados" in result_2["message"]["content"].lower()
        or "pregunta" in result_2["message"]["content"].lower()
    )


@pytest.mark.integration
def test_test_generation_without_previous_context(
    api_base_url, api_timeout, auth_token
):
    """
    Verifica que se puede generar un test sin haber buscado nada previamente,
    gracias a la recuperación proactiva.
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    new_session = f"test-proactive-{uuid.uuid4()}"

    payload = {
        "query": "Quiero repasar Git con un test",
        "id": new_session,
        "asignatura": "iv",
    }

    response = requests.post(
        f"{api_base_url}/chat", json=payload, headers=headers, timeout=api_timeout
    )

    assert response.status_code == 200
    result = response.json()
    content = result["message"]["content"]

    # Debe contener la mención a la recopilación de información o la pregunta sobre Git
    assert any(
        term in content.lower()
        for term in ["git", "rama", "repositorio", "commit", "checkout", "vcs"]
    )
    assert "información" in content.lower() or "pregunta" in content.lower()
