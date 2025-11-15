"""Integration tests for RAG service."""

import os
import time

import pytest
import requests


@pytest.fixture(scope="session", autouse=True)
def verify_rag_api_available(rag_api_base_url):
    """Verify that RAG API is available before running tests."""
    max_retries = 30
    retry_delay = 2

    print(f"\nVerifying RAG API availability at {rag_api_base_url}...")

    for attempt in range(max_retries):
        try:
            response = requests.get(f"{rag_api_base_url}/health", timeout=5)
            if response.status_code == 200:
                print(f"✓ RAG API available at {rag_api_base_url}")
                return
        except (requests.ConnectionError, requests.Timeout):
            if attempt < max_retries - 1:
                print(
                    f"Attempt {attempt + 1}/{max_retries} - RAG API not available, retrying in {retry_delay}s..."
                )
                time.sleep(retry_delay)
            else:
                raise

    pytest.fail(
        f"RAG API not available at {rag_api_base_url} after {max_retries} attempts. "
        "Ensure containers are running with 'docker-compose up -d'"
    )


@pytest.fixture(scope="session")
def rag_api_base_url():
    """Fixture providing the RAG API base URL."""
    return os.getenv("RAG_API_BASE_URL", "http://localhost:8081")


@pytest.fixture(scope="session")
def api_timeout():
    """Timeout for HTTP requests to the API."""
    return int(os.getenv("API_TIMEOUT", "30"))


@pytest.mark.integration
def test_health_endpoint(rag_api_base_url, api_timeout):
    """Test that health endpoint returns healthy status."""
    response = requests.get(f"{rag_api_base_url}/health", timeout=api_timeout)
    assert response.status_code == 200

    data = response.json()
    assert "status" in data
    assert "qdrant_connected" in data
    assert data["qdrant_connected"] is True


@pytest.mark.integration
def test_root_endpoint(rag_api_base_url, api_timeout):
    """Test root endpoint returns API information."""
    response = requests.get(f"{rag_api_base_url}/", timeout=api_timeout)
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "RAG Service"
    assert data["status"] == "running"


@pytest.mark.integration
def test_collection_info(rag_api_base_url, api_timeout):
    """Test getting collection information."""
    response = requests.get(f"{rag_api_base_url}/collection/info", timeout=api_timeout)
    assert response.status_code == 200

    data = response.json()
    assert "name" in data
    assert "points_count" in data
    assert "status" in data


@pytest.mark.integration
def test_index_and_search_documents(rag_api_base_url, api_timeout):
    """Test full workflow: index documents and search."""
    # Index documents
    documents = [
        {
            "content": "Introduction to fuzzy logic and fuzzy sets. Fuzzy logic is a mathematical approach.",
            "metadata": {
                "asignatura": "Test Subject",
                "tipo_documento": "apuntes",
                "fecha": "2025-11-04",
                "tema": "Introduction",
            },
        },
        {
            "content": "Fuzzy membership functions define the degree of membership in fuzzy sets.",
            "metadata": {
                "asignatura": "Test Subject",
                "tipo_documento": "apuntes",
                "fecha": "2025-11-04",
                "tema": "Membership Functions",
            },
        },
        {
            "content": "Applications of fuzzy logic in control systems and decision making.",
            "metadata": {
                "asignatura": "Test Subject",
                "tipo_documento": "ejercicios",
                "fecha": "2025-11-04",
                "tema": "Applications",
            },
        },
    ]

    index_response = requests.post(
        f"{rag_api_base_url}/index", json=documents, timeout=api_timeout
    )
    assert index_response.status_code == 200
    index_data = index_response.json()
    assert index_data["indexed_count"] >= len(documents)

    # Wait a moment for indexing to complete
    time.sleep(2)

    # Search for relevant documents
    search_payload = {
        "query": "fuzzy logic introduction",
        "top_k": 5,
        "similarity_threshold": 0.3,
    }

    search_response = requests.post(
        f"{rag_api_base_url}/search", json=search_payload, timeout=api_timeout
    )
    assert search_response.status_code == 200
    search_data = search_response.json()

    assert "results" in search_data
    assert search_data["total_results"] > 0
    assert search_data["query"] == "fuzzy logic introduction"

    # Verify results have expected structure
    for result in search_data["results"]:
        assert "content" in result
        assert "metadata" in result
        assert "score" in result
        assert result["score"] > 0


@pytest.mark.integration
def test_search_with_filters(rag_api_base_url, api_timeout):
    """Test search with subject and document type filters."""
    search_payload = {
        "query": "fuzzy membership",
        "asignatura": "Test Subject",
        "tipo_documento": "apuntes",
        "top_k": 3,
    }

    response = requests.post(
        f"{rag_api_base_url}/search", json=search_payload, timeout=api_timeout
    )
    assert response.status_code == 200
    data = response.json()

    assert "results" in data
    # All results should match the filters
    for result in data["results"]:
        if "asignatura" in result["metadata"]:
            assert result["metadata"]["asignatura"] == "Test Subject"


@pytest.mark.integration
def test_search_no_results(rag_api_base_url, api_timeout):
    """Test search with query that returns no results."""
    search_payload = {
        "query": "xyzabc nonexistent topic qwerty",
        "top_k": 5,
        "similarity_threshold": 0.9,
    }

    response = requests.post(
        f"{rag_api_base_url}/search", json=search_payload, timeout=api_timeout
    )
    assert response.status_code == 200
    data = response.json()

    assert data["total_results"] == 0
    assert data["results"] == []


@pytest.mark.integration
def test_list_subjects(rag_api_base_url, api_timeout):
    """Test listing available subjects."""
    response = requests.get(f"{rag_api_base_url}/subjects", timeout=api_timeout)
    assert response.status_code == 200

    data = response.json()
    assert "subjects" in data
    assert "total_subjects" in data
    assert isinstance(data["subjects"], list)


@pytest.mark.integration
def test_list_files(rag_api_base_url, api_timeout):
    """Test listing files endpoint."""
    response = requests.get(f"{rag_api_base_url}/files", timeout=api_timeout)
    assert response.status_code == 200

    data = response.json()
    assert "files" in data
    assert "total_files" in data
    assert isinstance(data["files"], list)


@pytest.mark.integration
def test_invalid_search_payload(rag_api_base_url, api_timeout):
    """Test search with invalid payload."""
    invalid_payload = {"top_k": "invalid"}  # Should be int

    response = requests.post(
        f"{rag_api_base_url}/search", json=invalid_payload, timeout=api_timeout
    )
    assert response.status_code == 422  # Unprocessable Entity


@pytest.mark.integration
def test_invalid_index_payload(rag_api_base_url, api_timeout):
    """Test indexing with invalid document structure."""
    invalid_documents = [
        {
            "content": "Test content"
            # Missing required metadata field
        }
    ]

    response = requests.post(
        f"{rag_api_base_url}/index", json=invalid_documents, timeout=api_timeout
    )
    assert response.status_code == 422  # Unprocessable Entity


@pytest.mark.integration
def test_search_similarity_threshold(rag_api_base_url, api_timeout):
    """Test that similarity threshold filters results properly."""
    # Search with low threshold
    low_threshold_payload = {
        "query": "fuzzy logic",
        "top_k": 10,
        "similarity_threshold": 0.1,
    }

    low_response = requests.post(
        f"{rag_api_base_url}/search", json=low_threshold_payload, timeout=api_timeout
    )
    assert low_response.status_code == 200
    low_data = low_response.json()
    low_count = low_data["total_results"]

    # Search with high threshold
    high_threshold_payload = {
        "query": "fuzzy logic",
        "top_k": 10,
        "similarity_threshold": 0.8,
    }

    high_response = requests.post(
        f"{rag_api_base_url}/search", json=high_threshold_payload, timeout=api_timeout
    )
    assert high_response.status_code == 200
    high_data = high_response.json()
    high_count = high_data["total_results"]

    # High threshold should return fewer or equal results
    assert high_count <= low_count

    # All results should meet threshold
    for result in high_data["results"]:
        assert result["score"] >= 0.8
