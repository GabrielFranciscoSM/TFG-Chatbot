"""
FAQ Generation Service.

Handles extracting student questions from MongoDB and preparing them
for the FAQ generation pipeline (clustering and NLP).
"""

import logging
from typing import Any

import numpy as np
from pymongo import MongoClient

from math_service.config import settings
from math_service.services.clustering import get_closest_to_centroid, get_optimal_k
from math_service.services.fcm import SphericalFuzzyCMeans
from math_service.services.nlp_client import OllamaClient

logger = logging.getLogger(__name__)


class FAQService:
    """Service to handle FAQ generation pipeline data extraction."""

    CONVERSATIONS_COLLECTION = "conversations"

    def __init__(self, db_client: MongoClient | None = None):
        """Initialize with an optional MongoDB client."""
        if db_client:
            self.client = db_client
            self._owns_client = False
        else:
            self.client = MongoClient(settings.get_mongo_uri())
            self._owns_client = True

        self.db = self.client[settings.db_name]
        self.collection = self.db[self.CONVERSATIONS_COLLECTION]
        self.faq_collection = self.db["faqs"]
        self.nlp_client = OllamaClient()

    def close(self):
        """Close the database client if owned."""
        if self._owns_client:
            self.client.close()

    def gather_student_questions(
        self, subject: str | None = None, limit: int = 1000
    ) -> list[str]:
        """
        Retrieve student questions from MongoDB.

        Args:
            subject: Optional subject to filter questions by.
            limit: Maximum number of questions to retrieve.

        Returns:
            A list of question strings extracted from conversation turns.
        """
        query: dict[str, Any] = {}
        if subject:
            query["subject"] = subject

        # We only want actual questions from students, not test answers or empty queries
        # The schema implies 'query' stores the user's input.
        query["query"] = {"$exists": True, "$ne": "", "$type": "string"}

        # Optional: Exclude test sessions if we only want genuine organic questions
        query["was_test"] = {"$ne": True}

        try:
            # We sort by timestamp descending to get the most recent ones
            cursor = (
                self.collection.find(query, {"query": 1, "_id": 0})
                .sort("timestamp", -1)
                .limit(limit)
            )

            # Extract the query strings, filtering out really short ones
            # or inputs that might just be "yes", "ok"
            questions = []
            for doc in cursor:
                text = doc.get("query", "").strip()
                # A simple heuristic: real questions are usually more than a few characters
                if len(text) > 5:
                    questions.append(text)

            logger.info(
                f"Gathered {len(questions)} student questions "
                f"(subject={subject or 'all'})"
            )
            return questions

        except Exception as e:
            logger.error(f"Error extracting student questions: {e}")
            return []

    def generate_faqs(
        self, subject: str | None = None, min_cluster_size: int = 3
    ) -> dict[str, Any]:
        """
        Full FAQ pipeline entrypoint (stub).

        This will eventually use `math_investigation` to:
        1. Gather questions
        2. Clean text, extract embeddings
        3. Cluster questions
        4. Extract topics and select representative FAQs

        Args:
            subject: The subject to generate FAQs for.

        Returns:
            A dictionary containing the generated FAQ results and metadata.
        """
        questions = self.gather_student_questions(subject=subject)

        if not questions:
            return {
                "status": "error",
                "message": "No questions found to generate FAQs from.",
            }

        logger.info(f"Generating FAQs from {len(questions)} questions...")

        # 1. Fetch embeddings for all questions
        try:
            embeddings = self.nlp_client.get_embeddings_batch(questions)
        except Exception as e:
            logger.error(f"NLP service unavailable: {e}")
            return {"status": "error", "message": f"NLP service error: {e}"}

        if embeddings.shape[0] == 0:
            return {"status": "error", "message": "Failed to get embeddings"}

        # 2. Determine optimal k
        optimal_k = get_optimal_k(embeddings, max_k=min(15, len(questions) - 1))
        logger.info(f"Optimal number of clusters determined: {optimal_k}")

        # 3. Cluster the questions. Try SphericalFuzzyCMeans.
        fcm = SphericalFuzzyCMeans(n_clusters=optimal_k, random_state=42)
        fcm.fit(embeddings)

        # 4. Find the representative question for each cluster
        representative_indices = get_closest_to_centroid(
            X=embeddings, labels=fcm.labels_, centroids=fcm.centroids_
        )

        generated_faqs = []
        for i, idx in enumerate(representative_indices):
            # For now, we just select the representative question and leave answer empty
            # to be filled by a subject-matter expert or another system later.
            representative_question = questions[idx]

            # Count how many questions fell into this cluster
            cluster_size = int(np.sum(fcm.labels_ == i))

            if cluster_size < min_cluster_size:
                logger.info(
                    f"Skipping cluster {i} because size {cluster_size} < {min_cluster_size}"
                )
                continue

            faq_doc = {
                "question": representative_question,
                "answer": "",  # Answer extraction/generation could be added later
                "subject": subject or "general",
                "cluster_size": cluster_size,
                "created_at": __import__("datetime").datetime.now(
                    tz=__import__("datetime").timezone.utc
                ),
                "status": "draft",  # Needs review
            }
            generated_faqs.append(faq_doc)

        # 5. Save generated FAQs to MongoDB
        if generated_faqs:
            try:
                result = self.faq_collection.insert_many(generated_faqs)
                logger.info(f"Inserted {len(result.inserted_ids)} FAQs into MongoDB.")
            except Exception as e:
                logger.error(f"Failed to persist FAQs to MongoDB: {e}")

        return {
            "status": "success",
            "subject": subject,
            "questions_analyzed": len(questions),
            "clusters_formed": optimal_k,
            "faqs_generated": len(generated_faqs),
            "faqs": [f["question"] for f in generated_faqs],
        }
