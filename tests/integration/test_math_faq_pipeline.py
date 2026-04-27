"""
Integration tests for the FAQ generation pipeline.

Tests the full pipeline from question gathering through clustering
to FAQ generation, with mocked external services (MongoDB, Ollama).
"""

import unittest
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from math_service.services.faq_service import FAQService


@pytest.mark.integration
class TestFAQPipelineIntegration(unittest.TestCase):
    """Integration tests for the full FAQ generation pipeline."""

    def setUp(self):
        """Set up mocked MongoDB client and Ollama client."""
        self.mock_client = MagicMock()
        self.mock_db = MagicMock()
        self.mock_conversations = MagicMock()
        self.mock_faqs = MagicMock()

        self.mock_client.__getitem__.return_value = self.mock_db
        self.mock_db.__getitem__.side_effect = lambda name: (
            self.mock_conversations
            if name == FAQService.CONVERSATIONS_COLLECTION
            else self.mock_faqs
        )

        # Mock OllamaClient at module level
        self.ollama_patcher = patch("math_service.services.faq_service.OllamaClient")
        self.mock_ollama_cls = self.ollama_patcher.start()
        self.mock_ollama = MagicMock()
        self.mock_ollama_cls.return_value = self.mock_ollama

        self.service = FAQService(db_client=self.mock_client)

    def tearDown(self):
        self.ollama_patcher.stop()

    def _setup_questions_cursor(self, questions: list[dict]):
        """Helper to set up the MongoDB cursor chain: find().sort().limit()."""
        mock_find = MagicMock()
        mock_sort = MagicMock()
        mock_limit = MagicMock()

        self.mock_conversations.find.return_value = mock_find
        mock_find.sort.return_value = mock_sort
        mock_sort.limit.return_value = mock_limit
        mock_limit.__iter__.return_value = iter(questions)

    def test_full_pipeline_generates_faqs(self):
        """Test complete pipeline: questions → embeddings → clustering → FAQs."""
        # 1. Set up 6 questions that form 2 natural clusters
        questions = [
            {"query": "¿Cómo se calcula una derivada?"},
            {"query": "¿Qué es la derivada de x^2?"},
            {"query": "¿Cómo derivar una función compuesta?"},
            {"query": "¿Qué es una integral definida?"},
            {"query": "¿Cómo calcular el área bajo una curva?"},
            {"query": "¿Cuál es la integral de sen(x)?"},
        ]
        self._setup_questions_cursor(questions)

        # 2. Mock embeddings: cluster 1 near [1,0], cluster 2 near [0,1]
        embeddings = np.array(
            [
                [0.95, 0.05],
                [0.90, 0.10],
                [0.92, 0.08],
                [0.05, 0.95],
                [0.10, 0.90],
                [0.08, 0.92],
            ]
        )
        # Normalize for spherical K-means
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        embeddings = embeddings / norms
        self.mock_ollama.get_embeddings_batch.return_value = embeddings

        # 3. Mock insert_many response
        self.mock_faqs.insert_many.return_value = MagicMock(inserted_ids=["id1", "id2"])

        # 4. Run the pipeline
        with (
            patch(
                "math_service.services.faq_service.get_optimal_k_fcm", return_value=2
            ),
            patch(
                "math_service.services.faq_service.SphericalFuzzyCMeans"
            ) as mock_fcm_cls,
            patch(
                "math_service.services.faq_service.get_closest_to_centroid",
                return_value=[0, 3],
            ),
        ):
            mock_fcm = MagicMock()
            mock_fcm.labels_ = np.array([0, 0, 0, 1, 1, 1])
            mock_fcm.centroids_ = np.array([[1.0, 0.0], [0.0, 1.0]])
            mock_fcm_cls.return_value = mock_fcm

            result = self.service.generate_faqs(subject="Cálculo", min_cluster_size=2)

        # 5. Verify results
        assert result["status"] == "success"
        assert result["subject"] == "Cálculo"
        assert result["questions_analyzed"] == 6
        assert result["clusters_formed"] == 2
        assert result["faqs_generated"] == 2
        assert "¿Cómo se calcula una derivada?" in result["faqs"]
        assert "¿Qué es una integral definida?" in result["faqs"]

        # Verify persistence
        self.mock_faqs.insert_many.assert_called_once()
        inserted = self.mock_faqs.insert_many.call_args[0][0]
        assert len(inserted) == 2
        assert inserted[0]["subject"] == "Cálculo"
        assert inserted[0]["status"] == "draft"

    def test_pipeline_skips_small_clusters(self):
        """Test that clusters below min_cluster_size are excluded."""
        questions = [
            {"query": "¿Qué es una matriz?"},
            {"query": "¿Cómo multiplicar matrices?"},
            {"query": "¿Qué es el determinante?"},
            {"query": "¿Qué es un vector propio?"},  # Solo en cluster pequeño
        ]
        self._setup_questions_cursor(questions)

        embeddings = np.array([[0.9, 0.1], [0.85, 0.15], [0.88, 0.12], [0.1, 0.9]])
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        self.mock_ollama.get_embeddings_batch.return_value = embeddings / norms

        self.mock_faqs.insert_many.return_value = MagicMock(inserted_ids=["id1"])

        with (
            patch(
                "math_service.services.faq_service.get_optimal_k_fcm", return_value=2
            ),
            patch(
                "math_service.services.faq_service.SphericalFuzzyCMeans"
            ) as mock_fcm_cls,
            patch(
                "math_service.services.faq_service.get_closest_to_centroid",
                return_value=[0, 3],
            ),
        ):
            mock_fcm = MagicMock()
            mock_fcm.labels_ = np.array([0, 0, 0, 1])  # Cluster 1 has only 1
            mock_fcm.centroids_ = np.array([[1.0, 0.0], [0.0, 1.0]])
            mock_fcm_cls.return_value = mock_fcm

            result = self.service.generate_faqs(subject="Álgebra", min_cluster_size=2)

        assert result["status"] == "success"
        assert result["faqs_generated"] == 1  # Only cluster 0 passes threshold

    def test_pipeline_no_questions_returns_error(self):
        """Test that an empty question set returns an error."""
        self._setup_questions_cursor([])

        result = self.service.generate_faqs(subject="Vacía")

        assert result["status"] == "error"
        assert "No questions" in result["message"]
        self.mock_ollama.get_embeddings_batch.assert_not_called()

    def test_pipeline_ollama_failure_returns_error(self):
        """Test graceful handling when Ollama is unavailable."""
        questions = [
            {"query": "¿Pregunta de ejemplo uno?"},
            {"query": "¿Pregunta de ejemplo dos?"},
        ]
        self._setup_questions_cursor(questions)

        self.mock_ollama.get_embeddings_batch.side_effect = ConnectionError(
            "Ollama is down"
        )

        result = self.service.generate_faqs(subject="Error")

        assert result["status"] == "error"
        assert "NLP service error" in result["message"]
        self.mock_faqs.insert_many.assert_not_called()

    def test_pipeline_empty_embeddings_returns_error(self):
        """Test that empty embeddings result is properly handled."""
        questions = [
            {"query": "¿Alguna pregunta válida?"},
            {"query": "¿Otra pregunta válida?"},
        ]
        self._setup_questions_cursor(questions)

        self.mock_ollama.get_embeddings_batch.return_value = np.array([])

        result = self.service.generate_faqs(subject="SinEmbeddings")

        assert result["status"] == "error"
        assert "Failed to get embeddings" in result["message"]

    def test_pipeline_mongodb_persistence_failure_still_returns_result(self):
        """Test that MongoDB write failure doesn't crash the pipeline."""
        questions = [
            {"query": "¿Pregunta persistente uno?"},
            {"query": "¿Pregunta persistente dos?"},
            {"query": "¿Pregunta persistente tres?"},
        ]
        self._setup_questions_cursor(questions)

        embeddings = np.array([[0.9, 0.1], [0.85, 0.15], [0.88, 0.12]])
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        self.mock_ollama.get_embeddings_batch.return_value = embeddings / norms

        # Simulate MongoDB write failure
        self.mock_faqs.insert_many.side_effect = Exception("MongoDB write error")

        with (
            patch(
                "math_service.services.faq_service.get_optimal_k_fcm", return_value=1
            ),
            patch(
                "math_service.services.faq_service.SphericalFuzzyCMeans"
            ) as mock_fcm_cls,
            patch(
                "math_service.services.faq_service.get_closest_to_centroid",
                return_value=[0],
            ),
        ):
            mock_fcm = MagicMock()
            mock_fcm.labels_ = np.array([0, 0, 0])
            mock_fcm.centroids_ = np.array([[1.0, 0.0]])
            mock_fcm_cls.return_value = mock_fcm

            # Pipeline should still return success despite persistence failure
            result = self.service.generate_faqs(
                subject="Persistencia", min_cluster_size=2
            )

        assert result["status"] == "success"
        assert result["faqs_generated"] == 1
