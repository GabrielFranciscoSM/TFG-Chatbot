import pytest
import requests

@pytest.mark.integration
def test_chat_endpoint_basic_conversation(api_base_url, session_id, api_timeout):
    """Test básico de conversación con el chatbot a través de la API."""
    payload = {
        "query": "Hola, ¿cómo estás?",
        "id": session_id
    }
    
    response = requests.post(f"{api_base_url}/chat", json=payload, timeout=api_timeout)
    assert response.status_code == 200
    
    result = response.json()
    assert "messages" in result
    assert len(result["messages"]) >= 2
    
    last_msg = result["messages"][-1]
    assert "content" in last_msg


@pytest.mark.integration
def test_chat_endpoint_with_tools(api_base_url, session_id, api_timeout):
    """Test que verifica que el chatbot puede usar herramientas a través de la API."""
    payload = {
        "query": "¿Cuánto es 2 + 2?",
        "id": session_id
    }
    
    response = requests.post(f"{api_base_url}/chat", json=payload, timeout=api_timeout)
    assert response.status_code == 200
    
    result = response.json()
    assert "messages" in result
    # El LLM podría o no usar herramientas dependiendo del modelo
    assert len(result["messages"]) >= 2
    
    last_msg = result["messages"][-1]
    assert "content" in last_msg
    assert "4" in last_msg["content"]


@pytest.mark.integration
def test_chat_endpoint_with_memory(api_base_url, session_id, api_timeout):
    """Test que verifica que el chatbot mantiene memoria de la conversación."""
    # Primera interacción
    payload_1 = {
        "query": "Mi nombre es Alicia",
        "id": session_id
    }
    response_1 = requests.post(f"{api_base_url}/chat", json=payload_1, timeout=api_timeout)
    assert response_1.status_code == 200
    result_1 = response_1.json()
    assert "messages" in result_1
    
    # Segunda interacción - verificar que recuerda el nombre
    payload_2 = {
        "query": "¿Cuál es mi nombre?",
        "id": session_id
    }
    response_2 = requests.post(f"{api_base_url}/chat", json=payload_2, timeout=api_timeout)
    assert response_2.status_code == 200
    result_2 = response_2.json()
    assert "messages" in result_2
    
    last_msg = result_2["messages"][-1]
    assert "content" in last_msg
    assert "Alicia" in last_msg["content"]


@pytest.mark.integration
def test_chat_endpoint_empty_message(api_base_url, session_id, api_timeout):
    """Test que verifica el comportamiento con mensajes vacíos."""
    payload = {
        "query": "",
        "id": session_id
    }
    
    response = requests.post(f"{api_base_url}/chat", json=payload, timeout=api_timeout)
    assert response.status_code == 200
    
    result = response.json()
    assert "messages" in result


@pytest.mark.integration
def test_chat_endpoint_complex_calculation(api_base_url, session_id, api_timeout):
    """Test que verifica cálculos complejos a través de la API."""
    payload = {
        "query": "Calcula (15 * 3) + (20 / 4)",
        "id": session_id
    }
    
    response = requests.post(f"{api_base_url}/chat", json=payload, timeout=api_timeout)
    assert response.status_code == 200
    
    result = response.json()
    assert "messages" in result
    
    last_msg = result["messages"][-1]
    assert "content" in last_msg
    assert "50" in last_msg["content"]


@pytest.mark.integration
def test_chat_endpoint_invalid_payload(api_base_url, api_timeout):
    """Test que verifica el manejo de payloads inválidos."""
    # Payload sin campo requerido
    invalid_payload = {
        "query": "Hola"
        # Falta el campo 'id'
    }
    
    response = requests.post(f"{api_base_url}/chat", json=invalid_payload, timeout=api_timeout)
    assert response.status_code == 422  # Unprocessable Entity


@pytest.mark.integration
def test_chat_endpoint_different_sessions(api_base_url, session_id, api_timeout):
    """Test que verifica que diferentes sesiones mantienen contextos separados."""
    session_id_2 = f"test-session-different-{session_id}"
    
    # Primera sesión - establecer nombre
    payload_1 = {
        "query": "Mi nombre es Roberto",
        "id": session_id
    }
    requests.post(f"{api_base_url}/chat", json=payload_1, timeout=api_timeout)
    
    # Segunda sesión - establecer nombre diferente
    payload_2 = {
        "query": "Mi nombre es Carolina",
        "id": session_id_2
    }
    requests.post(f"{api_base_url}/chat", json=payload_2, timeout=api_timeout)
    
    # Verificar primera sesión
    payload_verify_1 = {
        "query": "¿Cuál es mi nombre?",
        "id": session_id
    }
    response_1 = requests.post(f"{api_base_url}/chat", json=payload_verify_1, timeout=api_timeout)
    result_1 = response_1.json()
    assert "Roberto" in result_1["messages"][-1]["content"]
    
    # Verificar segunda sesión
    payload_verify_2 = {
        "query": "¿Cuál es mi nombre?",
        "id": session_id_2
    }
    response_2 = requests.post(f"{api_base_url}/chat", json=payload_verify_2, timeout=api_timeout)
    result_2 = response_2.json()
    assert "Carolina" in result_2["messages"][-1]["content"]
