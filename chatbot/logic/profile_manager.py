"""
Student Profile Manager Module.

Manages persistence and updates of student knowledge profiles in MongoDB.
Tracks learning progress, topic mastery, and interaction history for
adaptive response generation.

Usage:
    from chatbot.logic.profile_manager import ProfileManager, get_profile_manager

    manager = get_profile_manager()
    manager.record_interaction(
        user_id="student123",
        query="¿Qué es Docker?",
        difficulty="intermediate",
        subject="iv",
        topic="docker"
    )
    profile = manager.get_profile("student123")
"""

import logging
from datetime import UTC, datetime
from typing import Any

from chatbot.db.mongo import MongoDBClient
from chatbot.logic.models.student_profile import (
    ConversationTurn,
    Interaction,
    StudentProfile,
)

logger = logging.getLogger(__name__)


# Maximum number of recent interactions to keep in profile
MAX_RECENT_INTERACTIONS = 50


class ProfileManager:
    """
    Manager for student knowledge profiles in MongoDB.

    Handles CRUD operations and mastery calculations for student profiles.
    Uses atomic MongoDB operations for safe concurrent updates.

    Attributes:
        PROFILES_COLLECTION: Name of MongoDB collection for profiles
        CONVERSATIONS_COLLECTION: Name of MongoDB collection for full conversations
    """

    PROFILES_COLLECTION = "student_profiles"
    CONVERSATIONS_COLLECTION = "conversations"

    def __init__(self, db_client: MongoDBClient | None = None):
        """Initialize ProfileManager with optional MongoDB client.

        Args:
            db_client: Optional MongoDB client. If not provided, creates a new one.
        """
        self._db_client = db_client
        self._owns_client = db_client is None

    @property
    def db_client(self) -> MongoDBClient:
        """Lazy initialization of MongoDB client."""
        if self._db_client is None:
            self._db_client = MongoDBClient()
        return self._db_client

    def get_profile(self, user_id: str) -> StudentProfile | None:
        """Retrieve a student's profile.

        Args:
            user_id: Unique user identifier

        Returns:
            StudentProfile if found, None otherwise
        """
        try:
            collection = self.db_client.get_collection(self.PROFILES_COLLECTION)
            doc = collection.find_one({"_id": user_id})
            if doc:
                # Map _id to user_id for Pydantic model
                doc["user_id"] = doc.pop("_id")
                return StudentProfile(**doc)
            return None
        except Exception as e:
            logger.warning(f"Failed to get profile for {user_id}: {e}")
            return None

    def get_or_create_profile(self, user_id: str) -> StudentProfile:
        """Get existing profile or create a new one.

        Args:
            user_id: Unique user identifier

        Returns:
            Existing or newly created StudentProfile
        """
        profile = self.get_profile(user_id)
        if profile:
            return profile

        # Create new profile
        now = datetime.now(UTC)
        new_profile = StudentProfile(
            user_id=user_id,
            created_at=now,
            updated_at=now,
        )

        try:
            collection = self.db_client.get_collection(self.PROFILES_COLLECTION)
            doc = new_profile.model_dump()
            doc["_id"] = doc.pop("user_id")
            collection.insert_one(doc)
            logger.info(f"Created new profile for user {user_id}")
            return new_profile
        except Exception as e:
            logger.warning(f"Failed to create profile for {user_id}: {e}")
            # Return the profile anyway (might be memory-only)
            return new_profile

    def record_interaction(
        self,
        user_id: str,
        query: str,
        difficulty: str = "unknown",
        subject: str | None = None,
        topic: str | None = None,
        was_test: bool = False,
        test_score: float | None = None,
    ) -> bool:
        """Record a learning interaction and update profile.

        Updates the student's profile with the new interaction data,
        including difficulty distribution and topic mastery if applicable.

        Args:
            user_id: Unique user identifier
            query: User's question or input
            difficulty: Classified difficulty level
            subject: Subject/course context
            topic: Extracted topic from interaction
            was_test: Whether this was a test session
            test_score: Test score as ratio (0-1) if applicable

        Returns:
            True if successfully recorded, False otherwise
        """
        try:
            collection = self.db_client.get_collection(self.PROFILES_COLLECTION)

            now = datetime.now(UTC)
            interaction = Interaction(
                timestamp=now,
                query=query,
                difficulty=difficulty,
                topic=topic,
                subject=subject,
                was_test=was_test,
                test_score=test_score,
            )

            # Build atomic update operations
            update_ops: dict[str, Any] = {
                "$set": {"updated_at": now},
                "$inc": {"total_interactions": 1},
                "$push": {
                    "recent_interactions": {
                        "$each": [interaction.model_dump()],
                        "$slice": -MAX_RECENT_INTERACTIONS,  # Keep only last N
                    }
                },
            }

            # Update difficulty distribution if known
            if difficulty in ("basic", "intermediate", "advanced"):
                update_ops["$inc"][f"difficulty_distribution.{difficulty}"] = 1

            # Update topic mastery if we have subject and topic
            if subject and topic:
                mastery_path = f"subject_mastery.{subject}.{topic}"
                # Use dot notation for nested updates
                update_ops["$inc"][f"{mastery_path}.interactions_count"] = 1
                update_ops["$set"][f"{mastery_path}.last_interaction"] = now

                # Initialize mastery level if not exists (done via upsert with setOnInsert)
                if "$setOnInsert" not in update_ops:
                    update_ops["$setOnInsert"] = {}
                update_ops["$setOnInsert"][f"{mastery_path}.level"] = 0.5
                update_ops["$setOnInsert"][f"{mastery_path}.correct_answers"] = 0
                update_ops["$setOnInsert"][f"{mastery_path}.total_test_questions"] = 0

            # Handle test score updates
            if was_test and test_score is not None:
                update_ops["$inc"]["total_tests_taken"] = 1
                # Note: average_test_score requires a separate calculation
                # We'll update it after getting the current value

            # Perform upsert (create profile if doesn't exist)
            result = collection.update_one(
                {"_id": user_id},
                update_ops,
                upsert=True,
            )

            # Update average test score if this was a test
            if was_test and test_score is not None:
                self._update_average_test_score(user_id, test_score)

            logger.debug(f"Recorded interaction for {user_id}: {difficulty}/{topic}")
            return result.modified_count > 0 or result.upserted_id is not None

        except Exception as e:
            logger.warning(f"Failed to record interaction for {user_id}: {e}")
            return False

    def _update_average_test_score(self, user_id: str, new_score: float) -> None:
        """Update the running average test score.

        Uses incremental average calculation to avoid re-reading all scores.

        Args:
            user_id: Unique user identifier
            new_score: New test score (0-1)
        """
        try:
            collection = self.db_client.get_collection(self.PROFILES_COLLECTION)
            doc = collection.find_one(
                {"_id": user_id}, {"total_tests_taken": 1, "average_test_score": 1}
            )

            if doc:
                total_tests = doc.get("total_tests_taken", 1)
                current_avg = doc.get("average_test_score")

                if current_avg is None:
                    new_avg = new_score
                else:
                    # Incremental average: new_avg = old_avg + (new_value - old_avg) / n
                    new_avg = current_avg + (new_score - current_avg) / total_tests

                collection.update_one(
                    {"_id": user_id},
                    {"$set": {"average_test_score": new_avg}},
                )
        except Exception as e:
            logger.warning(f"Failed to update test score average for {user_id}: {e}")

    def update_topic_mastery(
        self,
        user_id: str,
        subject: str,
        topic: str,
        correct: bool,
    ) -> bool:
        """Update topic mastery based on test question result.

        Adjusts mastery level based on correct/incorrect answers using
        a simple exponential moving average approach.

        Args:
            user_id: Unique user identifier
            subject: Subject/course identifier
            topic: Topic being tested
            correct: Whether the answer was correct

        Returns:
            True if successfully updated, False otherwise
        """
        try:
            collection = self.db_client.get_collection(self.PROFILES_COLLECTION)

            mastery_path = f"subject_mastery.{subject}.{topic}"
            now = datetime.now(UTC)

            # Get current mastery level
            doc = collection.find_one({"_id": user_id}, {mastery_path: 1})

            current_level = 0.5  # Default starting level
            if doc:
                subject_data = doc.get("subject_mastery", {})
                topic_data = subject_data.get(subject, {}).get(topic, {})
                current_level = topic_data.get("level", 0.5)

            # Adjust mastery: +0.1 for correct, -0.05 for incorrect
            # Asymmetric to encourage progress while penalizing errors less
            adjustment = 0.1 if correct else -0.05
            new_level = max(0.0, min(1.0, current_level + adjustment))

            update_ops: dict[str, Any] = {
                "$set": {
                    f"{mastery_path}.level": new_level,
                    f"{mastery_path}.last_interaction": now,
                    "updated_at": now,
                },
                "$inc": {
                    f"{mastery_path}.total_test_questions": 1,
                },
            }

            if correct:
                update_ops["$inc"][f"{mastery_path}.correct_answers"] = 1

            result = collection.update_one(
                {"_id": user_id},
                update_ops,
                upsert=True,
            )

            logger.debug(
                f"Updated mastery for {user_id}/{subject}/{topic}: "
                f"{current_level:.2f} -> {new_level:.2f} (correct={correct})"
            )
            return result.modified_count > 0 or result.upserted_id is not None

        except Exception as e:
            logger.warning(f"Failed to update topic mastery: {e}")
            return False

    def save_conversation_turn(
        self,
        session_id: str,
        query: str,
        answer: str,
        user_id: str | None = None,
        subject: str | None = None,
        difficulty: str | None = None,
        latency_ms: float | None = None,
        rag_sources_used: list[str] | None = None,
        was_test: bool = False,
    ) -> str | None:
        """Save a full conversation turn for later analysis.

        Stores the complete question and answer without truncation,
        along with metadata for research and analytics purposes.

        Args:
            session_id: Chat session identifier
            query: User's question
            answer: Full chatbot response (not truncated)
            user_id: Optional user identifier
            subject: Optional subject context
            difficulty: Optional classified difficulty level
            latency_ms: Optional response time in milliseconds
            rag_sources_used: Optional list of RAG sources consulted
            was_test: Whether part of a test session

        Returns:
            Inserted document ID or None if failed
        """
        try:
            collection = self.db_client.get_collection(self.CONVERSATIONS_COLLECTION)

            turn = ConversationTurn(
                session_id=session_id,
                user_id=user_id,
                subject=subject,
                query=query,
                answer=answer,
                difficulty=difficulty,
                latency_ms=latency_ms,
                rag_sources_used=rag_sources_used,
                was_test=was_test,
            )

            result = collection.insert_one(turn.model_dump())
            logger.debug(f"Saved conversation turn for session {session_id}")
            return str(result.inserted_id)

        except Exception as e:
            logger.warning(f"Failed to save conversation turn: {e}")
            return None

    def get_conversation_history(
        self,
        session_id: str | None = None,
        user_id: str | None = None,
        limit: int = 100,
    ) -> list[ConversationTurn]:
        """Retrieve conversation history by session or user.

        Args:
            session_id: Optional session filter
            user_id: Optional user filter
            limit: Maximum number of turns to return

        Returns:
            List of ConversationTurn records
        """
        try:
            collection = self.db_client.get_collection(self.CONVERSATIONS_COLLECTION)

            query: dict[str, Any] = {}
            if session_id:
                query["session_id"] = session_id
            if user_id:
                query["user_id"] = user_id

            cursor = collection.find(query).sort("timestamp", -1).limit(limit)
            return [ConversationTurn(**doc) for doc in cursor]

        except Exception as e:
            logger.warning(f"Failed to get conversation history: {e}")
            return []

    def close(self):
        """Close the database connection if we own it."""
        if self._owns_client and self._db_client is not None:
            self._db_client.close()


# Global profile manager instance for convenience
_profile_manager: ProfileManager | None = None


def get_profile_manager() -> ProfileManager:
    """Get or create the global ProfileManager instance."""
    global _profile_manager
    if _profile_manager is None:
        _profile_manager = ProfileManager()
    return _profile_manager
