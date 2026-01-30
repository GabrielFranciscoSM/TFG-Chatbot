"""Tests for the query complexity classifier."""

import pytest

from chatbot.logic.query_classifier import (
    COMPLEX_KEYWORDS_EN,
    COMPLEX_KEYWORDS_ES,
    COMPLEX_PATTERNS,
    QueryComplexity,
    classify_query,
)


class TestQueryClassifier:
    """Test suite for query classification."""

    @pytest.mark.parametrize(
        "query",
        [
            "Hola",
            "Buenos días",
            "Gracias",
            "Hello",
            "Hi",
            "Thanks",
            "Adiós",
        ],
    )
    def test_greetings_are_simple(self, query: str):
        """Greetings should be classified as simple."""
        assert classify_query(query) == QueryComplexity.SIMPLE

    @pytest.mark.parametrize(
        "query",
        [
            "¿Cuándo es el examen?",
            "¿Dónde está el aula?",
            "¿Quién es el profesor?",
            "When is the deadline?",
            "Where is the classroom?",
        ],
    )
    def test_factual_questions_are_simple(self, query: str):
        """Simple factual questions should be classified as simple."""
        assert classify_query(query) == QueryComplexity.SIMPLE

    @pytest.mark.parametrize(
        "query",
        [
            "¿Por qué usamos Docker en lugar de máquinas virtuales?",
            "Explica el concepto de contenedores",
            "¿Cuál es la diferencia entre REST y GraphQL?",
            "¿Cómo funciona el garbage collector?",
            "Why is Docker better than VMs?",
            "Explain how containers work",
            "What is the difference between REST and GraphQL?",
            "How does the garbage collector work?",
        ],
    )
    def test_complex_questions_detected(self, query: str):
        """Complex conceptual questions should be classified as complex."""
        assert classify_query(query) == QueryComplexity.COMPLEX

    @pytest.mark.parametrize(
        "query",
        [
            "Compara Docker con Podman",
            "¿Cuáles son las ventajas y desventajas de microservicios?",
            "Analiza este código",
            "¿Cómo puedo solucionar este error?",
            "Compare Python and Java",
            "What are the pros and cons of microservices?",
        ],
    )
    def test_analytical_questions_are_complex(self, query: str):
        """Analytical and comparative questions should be complex."""
        assert classify_query(query) == QueryComplexity.COMPLEX

    def test_long_queries_default_to_complex(self):
        """Long unclassified queries should default to complex."""
        long_query = "Tengo una duda sobre un tema muy específico que me gustaría que me ayudaras a entender mejor porque es bastante complicado"
        assert classify_query(long_query) == QueryComplexity.COMPLEX

    def test_short_queries_default_to_simple(self):
        """Short unclassified queries should default to simple."""
        assert classify_query("ok") == QueryComplexity.SIMPLE

    def test_case_insensitivity(self):
        """Classification should be case insensitive."""
        assert classify_query("POR QUÉ funciona así?") == QueryComplexity.COMPLEX
        assert classify_query("HOLA") == QueryComplexity.SIMPLE

    def test_complex_keywords_lists_not_empty(self):
        """Ensure keyword lists are populated."""
        assert len(COMPLEX_KEYWORDS_ES) > 10
        assert len(COMPLEX_KEYWORDS_EN) > 10
        assert len(COMPLEX_PATTERNS) > 3
