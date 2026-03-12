"""
Integration tests for the Topic Extraction pipeline.

Tests the full pipeline from chunk retrieval through TF-IDF/NMF
to topic extraction, with mocked external services (RAG, Mistral, MongoDB).
"""

import json
import unittest
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from math_service.services.topic_service import TopicService


def _make_rag_response(chunks: list[str]) -> bytes:
    """Build a fake RAG service response."""
    results = [{"content": chunk} for chunk in chunks]
    return json.dumps({"results": results}).encode("utf-8")


@pytest.mark.integration
class TestTopicPipelineIntegration(unittest.TestCase):
    """Integration tests for the full topic extraction pipeline."""

    def setUp(self):
        """Set up mocked MongoDB, Ollama, and Mistral clients."""
        self.mock_client = MagicMock()
        self.mock_db = MagicMock()
        self.mock_collection = MagicMock()

        self.mock_client.__getitem__.return_value = self.mock_db
        self.mock_db.__getitem__.return_value = self.mock_collection

        # Patch external clients at module level
        self.ollama_patcher = patch("math_service.services.topic_service.OllamaClient")
        self.mistral_patcher = patch(
            "math_service.services.topic_service.MistralClient"
        )

        self.mock_ollama_cls = self.ollama_patcher.start()
        self.mock_mistral_cls = self.mistral_patcher.start()

        self.mock_ollama = MagicMock()
        self.mock_mistral = MagicMock()
        self.mock_ollama_cls.return_value = self.mock_ollama
        self.mock_mistral_cls.return_value = self.mock_mistral

        self.service = TopicService(db_client=self.mock_client)

    def tearDown(self):
        self.ollama_patcher.stop()
        self.mistral_patcher.stop()

    def _mock_rag_response(self, chunks: list[str]):
        """Patch urllib to return fake RAG chunks."""
        mock_response = MagicMock()
        mock_response.read.return_value = _make_rag_response(chunks)
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        return mock_response

    def test_full_pipeline_extracts_topics_with_tfidf(self):
        """Test complete pipeline: chunks → TF-IDF → NMF → topics + concept map."""
        chunks = [
            "álgebra lineal vectores matrices determinantes espacios vectoriales",
            "matrices inversas sistemas ecuaciones lineales reducción gaussiana",
            "cálculo derivadas integrales límites funciones continuidad",
            "derivadas parciales gradiente divergencia campos vectoriales",
            "probabilidad estadística distribuciones muestreo varianza media",
            "distribuciones normal binomial poisson variables aleatorias",
        ]

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.return_value = self._mock_rag_response(chunks)

            # Mistral generates topic titles
            self.mock_mistral.generate_text.side_effect = [
                "Álgebra Lineal",
                "Cálculo Diferencial",
                "Estadística",
            ]

            result = self.service.extract_topics(
                subject="Matemáticas",
                vectorizer_type="tfidf",
                k=3,
                cost_function="frobenius",
            )

        # Verify base result
        assert result["status"] == "success"
        assert result["subject"] == "Matemáticas"
        assert result["source_chunks"] == 6
        assert result["clusters_formed"] == 3

        # Verify topics structure
        assert len(result["topics"]) > 0
        for topic in result["topics"]:
            assert "cluster" in topic
            assert "topic_name" in topic
            assert "terms" in topic
            assert "weight" in topic
            assert len(topic["terms"]) > 0

        # Verify concept map
        concept_map = result["concept_map"]
        assert "nodes" in concept_map
        assert "links" in concept_map
        # Should have at least the subject node + topic nodes
        subject_nodes = [n for n in concept_map["nodes"] if n["group"] == "subject"]
        assert len(subject_nodes) == 1
        assert subject_nodes[0]["id"] == "Matemáticas"

        topic_nodes = [n for n in concept_map["nodes"] if n["group"] == "topic"]
        assert len(topic_nodes) == len(result["topics"])

        term_nodes = [n for n in concept_map["nodes"] if n["group"] == "term"]
        assert len(term_nodes) > 0

        # Verify doc_topic_matrix
        assert "doc_topic_matrix" in result
        matrix = result["doc_topic_matrix"]
        assert len(matrix) == 6  # 6 docs
        assert len(matrix[0]) == 3  # 3 topics
        # Each row should sum to ~1 (normalized)
        for row in matrix:
            np.testing.assert_almost_equal(sum(row), 1.0, decimal=5)

        # Verify MongoDB persistence
        self.mock_collection.insert_one.assert_called_once()

    def test_full_pipeline_with_bow_vectorizer(self):
        """Test pipeline using BoW instead of TF-IDF."""
        chunks = [
            "algebra vectores matrices algebra calculo vectores",
            "calculo derivadas integrales derivadas algebra matrices",
            "probabilidad estadistica distribuciones calculo integrales vectores",
        ]

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.return_value = self._mock_rag_response(chunks)
            self.mock_mistral.generate_text.return_value = "Tema General"

            result = self.service.extract_topics(
                subject="Test", vectorizer_type="bow", k=2
            )

        assert result["status"] == "success"
        assert result["clusters_formed"] == 2

    def test_pipeline_auto_k_determination(self):
        """Test pipeline with automatic k determination."""
        chunks = [
            "algebra vectores matrices determinantes",
            "algebra lineal sistemas ecuaciones",
            "calculo derivadas integrales limites",
            "calculo diferencial gradiente divergencia",
        ]

        with (
            patch("urllib.request.urlopen") as mock_urlopen,
            patch("math_service.services.topic_service.get_optimal_k", return_value=2),
        ):
            mock_urlopen.return_value = self._mock_rag_response(chunks)
            self.mock_mistral.generate_text.return_value = "Tema"

            result = self.service.extract_topics(
                subject="AutoK", vectorizer_type="tfidf", k=None
            )

        assert result["status"] == "success"
        assert result["clusters_formed"] == 2

    def test_pipeline_rag_service_unavailable(self):
        """Test error handling when RAG service is down."""
        import urllib.error

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = urllib.error.URLError("Connection refused")

            result = self.service.extract_topics(subject="ErrorRAG")

        assert result["status"] == "error"
        assert "RAG service unavailable" in result["message"]
        self.mock_collection.insert_one.assert_not_called()

    def test_pipeline_no_chunks_returns_error(self):
        """Test error handling when no chunks are available."""
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.return_value = self._mock_rag_response([])

            result = self.service.extract_topics(subject="SinDocs")

        assert result["status"] == "error"
        assert "No chunks found" in result["message"]

    def test_pipeline_mistral_failure_uses_fallback_names(self):
        """Test that topic naming falls back to 'Tópico N' when Mistral fails."""
        chunks = [
            "algebra vectores matrices determinantes",
            "algebra lineal sistemas ecuaciones",
            "calculo derivadas integrales limites",
        ]

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.return_value = self._mock_rag_response(chunks)
            self.mock_mistral.generate_text.side_effect = RuntimeError(
                "Mistral API error"
            )

            result = self.service.extract_topics(subject="FallbackNames", k=2)

        assert result["status"] == "success"
        # Topic names should fall back to "Tópico N"
        for topic in result["topics"]:
            assert topic["topic_name"].startswith("Tópico")

    def test_pipeline_mongodb_persistence_failure_still_returns_result(self):
        """Test that MongoDB persistence error doesn't crash the pipeline."""
        chunks = [
            "álgebra lineal vectores matrices determinantes espacios vectoriales",
            "matrices inversas sistemas ecuaciones lineales reducción gaussiana",
            "cálculo derivadas integrales límites funciones continuidad",
            "derivadas parciales gradiente divergencia campos vectoriales",
        ]

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.return_value = self._mock_rag_response(chunks)
            self.mock_mistral.generate_text.return_value = "Tema"

            self.mock_collection.insert_one.side_effect = Exception(
                "MongoDB write error"
            )

            result = self.service.extract_topics(subject="PersistError", k=2)

        assert result["status"] == "success"
        assert len(result["topics"]) > 0
