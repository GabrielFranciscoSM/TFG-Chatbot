import unittest
from unittest.mock import MagicMock, patch

import numpy as np

from math_service.services.faq_service import FAQService


class TestFAQService(unittest.TestCase):
    def setUp(self):
        # Mock MongoClient
        self.mock_client = MagicMock()
        self.mock_db = MagicMock()
        self.mock_collection = MagicMock()
        self.mock_faq_collection = MagicMock()

        self.mock_client.__getitem__.return_value = self.mock_db
        self.mock_db.__getitem__.side_effect = lambda name: (
            self.mock_collection
            if name == FAQService.CONVERSATIONS_COLLECTION
            else self.mock_faq_collection
        )

        # Patch nlp_client creation
        self.patcher = patch("math_service.services.faq_service.OllamaClient")
        self.mock_ollama_class = self.patcher.start()
        self.mock_ollama = MagicMock()
        self.mock_ollama_class.return_value = self.mock_ollama

        self.service = FAQService(db_client=self.mock_client)

    def tearDown(self):
        self.patcher.stop()

    def test_gather_student_questions(self):
        # Mock cursor returned by collection.find
        mock_cursor = [
            {"query": "How do I calculate logarithms?"},
            {"query": "What is the derivative of x^2?"},
            {"query": "yes"},  # Should be filtered out
        ]

        # Setup the chain: find().sort().limit()
        mock_find = MagicMock()
        mock_sort = MagicMock()
        mock_limit = MagicMock()

        self.mock_collection.find.return_value = mock_find
        mock_find.sort.return_value = mock_sort
        mock_sort.limit.return_value = mock_limit

        # Return the actual documents when iterated
        mock_limit.__iter__.return_value = iter(mock_cursor)

        questions = self.service.gather_student_questions()

        self.assertEqual(len(questions), 2)
        self.assertEqual(questions[0], "How do I calculate logarithms?")
        self.assertEqual(questions[1], "What is the derivative of x^2?")

    @patch.object(FAQService, "gather_student_questions")
    def test_generate_faqs_no_questions(self, mock_gather):
        mock_gather.return_value = []

        result = self.service.generate_faqs()
        self.assertEqual(result["status"], "error")
        self.assertIn("No questions", result["message"])

    @patch.object(FAQService, "gather_student_questions")
    def test_generate_faqs_nlp_error(self, mock_gather):
        mock_gather.return_value = ["Q1", "Q2"]

        # Simulate NLP service failure
        self.mock_ollama.get_embeddings_batch.side_effect = Exception("Ollama is down")

        result = self.service.generate_faqs()

        self.assertEqual(result["status"], "error")
        self.assertIn("NLP service error", result["message"])

    @patch.object(FAQService, "gather_student_questions")
    def test_generate_faqs_min_cluster_size(self, mock_gather):
        mock_gather.return_value = ["Q1", "Q2", "Q3", "Q4"]

        # Mock embeddings
        mock_embeddings = np.array([[1.0, 0.0], [1.0, 0.0], [1.0, 0.0], [0.0, 1.0]])
        self.mock_ollama.get_embeddings_batch.return_value = mock_embeddings

        # Need to mock get_optimal_k and SphericalFuzzyCMeans
        with (
            patch("math_service.services.faq_service.get_optimal_k") as mock_optimal_k,
            patch(
                "math_service.services.faq_service.SphericalFuzzyCMeans"
            ) as mock_fcm_class,
            patch(
                "math_service.services.faq_service.get_closest_to_centroid"
            ) as mock_closest,
        ):

            mock_optimal_k.return_value = 2

            mock_fcm = MagicMock()
            mock_fcm.labels_ = np.array(
                [0, 0, 0, 1]
            )  # Cluster 0 has 3, Cluster 1 has 1
            mock_fcm.centroids_ = np.array([[1.0, 0.0], [0.0, 1.0]])
            mock_fcm_class.return_value = mock_fcm

            mock_closest.return_value = [0, 3]  # Representative indices

            # min_cluster_size is 3, so cluster 1 should be skipped
            result = self.service.generate_faqs(min_cluster_size=3)

            self.assertEqual(result["status"], "success")
            self.assertEqual(result["faqs_generated"], 1)
            self.assertEqual(result["faqs"][0], "Q1")
