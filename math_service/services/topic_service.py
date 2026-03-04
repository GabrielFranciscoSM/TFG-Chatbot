"""
Topic Extraction Service.

Handles extracting theoretical topics from documents via RAG service
and applying TF-IDF + clustering to find representative concepts.
"""

import json
import logging
import urllib.error
import urllib.request
from typing import Any

from math_service.config import settings
from math_service.services.clustering import get_optimal_k
from math_service.services.fcm import SphericalFuzzyCMeans
from math_service.services.nlp.tfidf import TFIDFVectorizer

logger = logging.getLogger(__name__)


class TopicService:
    """Service to handle Topic Extraction pipeline."""

    def __init__(self):
        """Initialize with RAG service configuration."""
        self.rag_url = settings.rag_service_url

    def get_subject_chunks(self, subject: str, top_k: int = 500) -> list[str]:
        """
        Fetch document chunks from the RAG service for a given subject.

        Args:
            subject: The subject to filter chunks by.
            top_k: Maximum number of chunks to retrieve.

        Returns:
            A list of text chunks.
        """
        url = f"{self.rag_url}/api/v1/search"
        payload = {
            "query": "conceptos clave temario",  # Dummy query to get semantic matches
            "asignatura": subject,
            "top_k": top_k,
            "similarity_threshold": 0.0,
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode("utf-8"))
                chunks = [item["content"] for item in result.get("results", [])]
                logger.info(f"Retrieved {len(chunks)} chunks for subject '{subject}'")
                return chunks
        except urllib.error.URLError as e:
            logger.error(f"Failed to fetch chunks from RAG service: {e}")
            raise ConnectionError(f"RAG service unavailable: {e}") from e
        except Exception as e:
            logger.error(f"Error extracting chunks: {e}")
            return []

    def extract_topics(self, subject: str) -> dict[str, Any]:
        """
        Extract representative topics for a subject from its chunks.

        Includes:
        1. Fetching chunks
        2. TF-IDF feature extraction
        3. Determining optimal K clusters
        4. Clustering and top terms extraction

        Args:
            subject: The subject to extract topics from.

        Returns:
            A dictionary containing topic metadata and extracted terms.
        """
        try:
            chunks = self.get_subject_chunks(subject)
        except ConnectionError as e:
            return {"status": "error", "message": str(e)}

        if not chunks:
            return {"status": "error", "message": "No chunks found for subject"}

        # 1. TF-IDF feature extraction
        vectorizer = TFIDFVectorizer(max_features=500, min_df=2)
        tfidf_matrix = vectorizer.fit_transform(chunks)
        feature_names = vectorizer.get_feature_names()

        if len(feature_names) == 0:
            return {"status": "error", "message": "Could not extract vocabulary"}

        # 2. Optimal K determination
        try:
            optimal_k = get_optimal_k(tfidf_matrix, max_k=min(10, len(chunks) - 1))
        except ValueError:
            optimal_k = 1

        # 3. Clustering
        fcm = SphericalFuzzyCMeans(n_clusters=optimal_k, random_state=42)
        fcm.fit(tfidf_matrix)

        # 4. Extract top terms for each centroid
        topics = []
        if fcm.centroids_ is not None:
            for i, centroid in enumerate(fcm.centroids_):
                # Sort centroid weights ascending, take last 5 (highest), reverse them
                top_indices = centroid.argsort()[-5:][::-1]
                top_terms = [
                    feature_names[idx] for idx in top_indices if centroid[idx] > 0
                ]
                if top_terms:
                    topics.append({"cluster": i, "terms": top_terms})

        return {
            "status": "success",
            "subject": subject,
            "clusters_formed": optimal_k,
            "topics": topics,
        }
