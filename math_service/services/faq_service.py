"""
FAQ Generation Service.

Handles extracting student questions from MongoDB and preparing them
for the FAQ generation pipeline (clustering and NLP).
"""

import logging
from typing import Any

from pymongo import MongoClient

from math_service.config import settings

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

    def generate_faqs(self, subject: str | None = None) -> dict[str, Any]:
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

        # TODO: Integrate with math_investigation NLP/Clustering here

        return {
            "status": "success",
            "subject": subject,
            "questions_analyzed": len(questions),
            "faqs": [],  # Placeholder for actual generated FAQs
            "message": "FAQ generation pipeline initiated (clustering stubbed)",
        }
