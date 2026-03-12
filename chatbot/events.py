"""
Pedagogical Events Module.

This module provides functionality for logging learning interaction events
to MongoDB. Events capture user behavior for analytics and research purposes.

Event Types:
    - question_asked: User sends a question to the chatbot
    - answer_received: Chatbot provides a response
    - rag_context_used: RAG retrieves relevant context
    - test_started: User begins a test session
    - test_completed: User finishes a test session

Example:
    from chatbot.events import EventLogger

    logger = EventLogger()
    logger.log_question_asked(
        session_id="abc123",
        user_id="user456",
        query="¿Qué es Docker?",
        subject_id="iv"
    )
"""

import logging
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from chatbot.db.mongo import MongoDBClient

logger = logging.getLogger(__name__)


class EventType(StrEnum):
    """Types of pedagogical events tracked by the system."""

    QUESTION_ASKED = "question_asked"
    ANSWER_RECEIVED = "answer_received"
    RAG_CONTEXT_USED = "rag_context_used"
    TEST_STARTED = "test_started"
    TEST_COMPLETED = "test_completed"


class EventLogger:
    """
    Logger for pedagogical events to MongoDB.

    This class provides methods to log various learning interaction events
    that can be used for analytics, research, and improving the chatbot.

    Attributes:
        collection_name: Name of the MongoDB collection for events
        db_client: MongoDB client instance
    """

    COLLECTION_NAME = "pedagogical_events"

    def __init__(self, db_client: MongoDBClient | None = None):
        """Initialize EventLogger with optional MongoDB client.

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

    def _log_event(
        self,
        event_type: EventType,
        session_id: str,
        user_id: str | None = None,
        subject_id: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> str | None:
        """Internal method to log a generic event.

        Args:
            event_type: Type of event to log
            session_id: Session/thread identifier
            user_id: Optional user identifier
            subject_id: Optional subject/course identifier
            payload: Optional event-specific data

        Returns:
            Inserted document ID or None if failed
        """
        try:
            collection = self.db_client.get_collection(self.COLLECTION_NAME)

            event_doc = {
                "event_type": event_type.value,
                "session_id": session_id,
                "user_id": user_id,
                "subject_id": subject_id,
                "timestamp": datetime.now(UTC),
                "payload": payload or {},
            }

            result = collection.insert_one(event_doc)
            logger.debug(f"Logged {event_type.value} event: {result.inserted_id}")
            return str(result.inserted_id)

        except Exception as e:
            logger.warning(f"Failed to log {event_type.value} event: {e}")
            return None

    def log_question_asked(
        self,
        session_id: str,
        query: str,
        user_id: str | None = None,
        subject_id: str | None = None,
    ) -> str | None:
        """Log when a user asks a question.

        Args:
            session_id: Session/thread identifier
            query: The question text
            user_id: Optional user identifier
            subject_id: Optional subject/course identifier

        Returns:
            Inserted document ID or None if failed
        """
        return self._log_event(
            event_type=EventType.QUESTION_ASKED,
            session_id=session_id,
            user_id=user_id,
            subject_id=subject_id,
            payload={"query": query},
        )

    def log_answer_received(
        self,
        session_id: str,
        answer: str,
        user_id: str | None = None,
        subject_id: str | None = None,
        latency_ms: float | None = None,
        store_full_answer: bool = False,
    ) -> str | None:
        """Log when the chatbot provides an answer.

        Args:
            session_id: Session/thread identifier
            answer: The response text
            user_id: Optional user identifier
            subject_id: Optional subject/course identifier
            latency_ms: Optional response latency in milliseconds
            store_full_answer: If True, store full answer; else truncate to 500 chars

        Returns:
            Inserted document ID or None if failed
        """
        # Truncate answer unless full storage requested
        if store_full_answer:
            stored_answer = answer
        else:
            stored_answer = answer[:500] + "..." if len(answer) > 500 else answer

        return self._log_event(
            event_type=EventType.ANSWER_RECEIVED,
            session_id=session_id,
            user_id=user_id,
            subject_id=subject_id,
            payload={"answer_preview": stored_answer, "latency_ms": latency_ms},
        )

    def log_rag_context_used(
        self,
        session_id: str,
        num_chunks: int,
        sources: list[str] | None = None,
        user_id: str | None = None,
        subject_id: str | None = None,
    ) -> str | None:
        """Log when RAG retrieves context for a query.

        Args:
            session_id: Session/thread identifier
            num_chunks: Number of document chunks retrieved
            sources: Optional list of source document names
            user_id: Optional user identifier
            subject_id: Optional subject/course identifier

        Returns:
            Inserted document ID or None if failed
        """
        return self._log_event(
            event_type=EventType.RAG_CONTEXT_USED,
            session_id=session_id,
            user_id=user_id,
            subject_id=subject_id,
            payload={"num_chunks": num_chunks, "sources": sources or []},
        )

    def log_test_started(
        self,
        session_id: str,
        topic: str,
        num_questions: int,
        difficulty: str,
        user_id: str | None = None,
        subject_id: str | None = None,
    ) -> str | None:
        """Log when a user starts a test session.

        Args:
            session_id: Session/thread identifier
            topic: Test topic
            num_questions: Number of questions in the test
            difficulty: Difficulty level
            user_id: Optional user identifier
            subject_id: Optional subject/course identifier

        Returns:
            Inserted document ID or None if failed
        """
        return self._log_event(
            event_type=EventType.TEST_STARTED,
            session_id=session_id,
            user_id=user_id,
            subject_id=subject_id,
            payload={
                "topic": topic,
                "num_questions": num_questions,
                "difficulty": difficulty,
            },
        )

    def log_test_completed(
        self,
        session_id: str,
        score: int,
        total: int,
        user_id: str | None = None,
        subject_id: str | None = None,
    ) -> str | None:
        """Log when a user completes a test session.

        Args:
            session_id: Session/thread identifier
            score: Number of correct answers
            total: Total number of questions
            user_id: Optional user identifier
            subject_id: Optional subject/course identifier

        Returns:
            Inserted document ID or None if failed
        """
        return self._log_event(
            event_type=EventType.TEST_COMPLETED,
            session_id=session_id,
            user_id=user_id,
            subject_id=subject_id,
            payload={"score": score, "total": total, "percentage": score / total * 100},
        )

    def close(self):
        """Close the database connection if we own it."""
        if self._owns_client and self._db_client is not None:
            self._db_client.close()


# Global event logger instance for convenience
_event_logger: EventLogger | None = None


def get_event_logger() -> EventLogger:
    """Get or create the global EventLogger instance."""
    global _event_logger
    if _event_logger is None:
        _event_logger = EventLogger()
    return _event_logger
