"""
Topic Extraction Service.

Handles extracting theoretical topics from documents via RAG service
and applying TF-IDF + clustering to find representative concepts.
"""

import datetime
import json
import logging
import urllib.error
import urllib.request
from typing import Any

import numpy as np
from pymongo import MongoClient

from math_service.config import settings
from math_service.services.clustering import get_optimal_k
from math_service.services.nlp.bow import BoWVectorizer
from math_service.services.nlp.nmf import NMF
from math_service.services.nlp.tfidf import TFIDFVectorizer

logger = logging.getLogger(__name__)


class TopicService:
    """Service to handle Topic Extraction pipeline."""

    def __init__(self, db_client: MongoClient | None = None):
        """Initialize with configuration and database client."""
        self.rag_url = settings.rag_service_url
        if db_client:
            self.client = db_client
            self._owns_client = False
        else:
            self.client = MongoClient(settings.get_mongo_uri())
            self._owns_client = True

        self.db = self.client[settings.db_name]
        self.collection = self.db["topic_results"]

    def close(self):
        """Close the database client if owned."""
        if self._owns_client:
            self.client.close()

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

    def extract_topics(
        self,
        subject: str,
        vectorizer_type: str = "tfidf",
        k: int | None = None,
        cost_function: str = "frobenius",
    ) -> dict[str, Any]:
        """
        Extract representative topics for a subject from its chunks.

        Includes:
        1. Fetching chunks
        2. TF-IDF or BoW feature extraction
        3. Determining optimal K clusters
        4. Clustering and top terms extraction

        Args:
            subject: The subject to extract topics from.
            vectorizer_type: 'tfidf' or 'bow' for feature extraction. Default is 'tfidf'.
            k: Optional number of topics. If not provided, determines optimal k.
            cost_function: Cost function for NMF ('frobenius' or 'kl').

        Returns:
            A dictionary containing topic metadata and extracted terms.
        """
        try:
            chunks = self.get_subject_chunks(subject)
        except ConnectionError as e:
            return {"status": "error", "message": str(e)}

        if not chunks:
            return {"status": "error", "message": "No chunks found for subject"}

        # 1. Feature extraction (TF-IDF or BoW)
        vectorizer: Any
        if vectorizer_type.lower() == "bow":
            vectorizer = BoWVectorizer(max_features=500, min_df=2)
        else:
            vectorizer = TFIDFVectorizer(max_features=500, min_df=2)

        feature_matrix = vectorizer.fit_transform(chunks)
        feature_names = vectorizer.get_feature_names()

        if len(feature_names) == 0:
            return {"status": "error", "message": "Could not extract vocabulary"}

        # 2. Optimal K determination
        if k is not None and k > 0:
            optimal_k = min(k, len(chunks))
        else:
            try:
                optimal_k = get_optimal_k(
                    feature_matrix, max_k=min(10, len(chunks) - 1)
                )
            except ValueError:
                optimal_k = 1

        # 3. NMF Topic Modeling
        # BoW values are >= 0 and TF-IDF are >= 0, so both work well with NMF KL and Frobenius.
        nmf = NMF(n_components=optimal_k, random_state=42, cost=cost_function)
        W, H = nmf.fit(feature_matrix)

        # 4. Extract top terms and build concept map
        topics = []
        nodes = []
        links = []

        # Add a central subject node
        nodes.append({"id": subject, "group": "subject", "label": subject})

        for i, row in enumerate(H):
            # Sort topic affinities for terms ascending, take last 5, reverse them
            top_indices = row.argsort()[-5:][::-1]
            top_terms = [feature_names[idx] for idx in top_indices if row[idx] > 0]

            topic_id = f"Tópico {i+1}"
            if top_terms:
                topics.append(
                    {
                        "cluster": i,
                        "topic_name": topic_id,
                        "terms": top_terms,
                        "weight": float(
                            np.sum(W[:, i])
                        ),  # Total importance of topic across docs
                    }
                )

                # Add topic to concept map
                nodes.append({"id": topic_id, "group": "topic", "label": topic_id})
                links.append({"source": subject, "target": topic_id, "value": 1.0})

                # Add terms and links
                for term_idx in top_indices:
                    term = feature_names[term_idx]
                    weight = float(row[term_idx])
                    if weight > 0:
                        term_id = f"term_{term}"
                        if not any(n["id"] == term_id for n in nodes):
                            nodes.append(
                                {"id": term_id, "group": "term", "label": term}
                            )
                        links.append(
                            {"source": topic_id, "target": term_id, "value": weight}
                        )

        concept_map = {"nodes": nodes, "links": links}

        result_doc = {
            "subject": subject,
            "clusters_formed": optimal_k,
            "topics": topics,
            "concept_map": concept_map,
            "created_at": datetime.datetime.now(tz=datetime.UTC),
            "source_chunks": len(chunks),
        }

        # 5. Persist to MongoDB
        try:
            self.collection.insert_one(result_doc.copy())
            logger.info(
                f"Persisted topic extraction results for '{subject}' to MongoDB."
            )
        except Exception as e:
            logger.error(f"Failed to persist topic results to MongoDB: {e}")

        result_doc["status"] = "success"
        # Remove MongoDB _id from returned dict if it was added inplace
        result_doc.pop("_id", None)
        return result_doc
