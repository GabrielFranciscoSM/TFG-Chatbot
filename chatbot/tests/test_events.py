"""
Tests for the Pedagogical Events module.

These tests verify that the EventLogger correctly logs events to MongoDB.
"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from chatbot.events import EventLogger, get_event_logger


class TestEventLogger:
    """Tests for the EventLogger class."""

    @pytest.fixture
    def mock_collection(self):
        """Create a mock MongoDB collection."""
        collection = MagicMock()
        collection.insert_one.return_value = MagicMock(inserted_id="test_id_123")
        return collection

    @pytest.fixture
    def mock_db_client(self, mock_collection):
        """Create a mock MongoDB client."""
        client = MagicMock()
        client.get_collection.return_value = mock_collection
        return client

    @pytest.fixture
    def event_logger(self, mock_db_client):
        """Create an EventLogger with mocked database."""
        return EventLogger(db_client=mock_db_client)

    def test_log_question_asked(self, event_logger, mock_collection):
        """Test logging a question_asked event."""
        result = event_logger.log_question_asked(
            session_id="session_123",
            query="¿Qué es Docker?",
            user_id="user_456",
            subject_id="iv",
        )

        assert result == "test_id_123"
        mock_collection.insert_one.assert_called_once()

        # Verify the document structure
        call_args = mock_collection.insert_one.call_args[0][0]
        assert call_args["event_type"] == "question_asked"
        assert call_args["session_id"] == "session_123"
        assert call_args["user_id"] == "user_456"
        assert call_args["subject_id"] == "iv"
        assert call_args["payload"]["query"] == "¿Qué es Docker?"
        assert isinstance(call_args["timestamp"], datetime)

    def test_log_answer_received(self, event_logger, mock_collection):
        """Test logging an answer_received event."""
        result = event_logger.log_answer_received(
            session_id="session_123",
            answer="Docker es una plataforma de contenedores...",
            user_id="user_456",
            subject_id="iv",
            latency_ms=1500.5,
        )

        assert result == "test_id_123"
        call_args = mock_collection.insert_one.call_args[0][0]
        assert call_args["event_type"] == "answer_received"
        assert call_args["payload"]["latency_ms"] == 1500.5

    def test_log_answer_received_truncates_long_answers(
        self, event_logger, mock_collection
    ):
        """Test that long answers are truncated to 500 chars."""
        long_answer = "A" * 600
        event_logger.log_answer_received(
            session_id="session_123",
            answer=long_answer,
        )

        call_args = mock_collection.insert_one.call_args[0][0]
        assert len(call_args["payload"]["answer_preview"]) == 503  # 500 + "..."
        assert call_args["payload"]["answer_preview"].endswith("...")

    def test_log_rag_context_used(self, event_logger, mock_collection):
        """Test logging a rag_context_used event."""
        result = event_logger.log_rag_context_used(
            session_id="session_123",
            num_chunks=5,
            sources=["doc1.pdf", "doc2.pdf"],
        )

        assert result == "test_id_123"
        call_args = mock_collection.insert_one.call_args[0][0]
        assert call_args["event_type"] == "rag_context_used"
        assert call_args["payload"]["num_chunks"] == 5
        assert call_args["payload"]["sources"] == ["doc1.pdf", "doc2.pdf"]

    def test_log_test_started(self, event_logger, mock_collection):
        """Test logging a test_started event."""
        result = event_logger.log_test_started(
            session_id="session_123",
            topic="Docker",
            num_questions=5,
            difficulty="medium",
        )

        assert result == "test_id_123"
        call_args = mock_collection.insert_one.call_args[0][0]
        assert call_args["event_type"] == "test_started"
        assert call_args["payload"]["topic"] == "Docker"
        assert call_args["payload"]["num_questions"] == 5
        assert call_args["payload"]["difficulty"] == "medium"

    def test_log_test_completed(self, event_logger, mock_collection):
        """Test logging a test_completed event."""
        result = event_logger.log_test_completed(
            session_id="session_123",
            score=4,
            total=5,
        )

        assert result == "test_id_123"
        call_args = mock_collection.insert_one.call_args[0][0]
        assert call_args["event_type"] == "test_completed"
        assert call_args["payload"]["score"] == 4
        assert call_args["payload"]["total"] == 5
        assert call_args["payload"]["percentage"] == 80.0

    def test_log_event_handles_db_error(self, event_logger, mock_collection):
        """Test that database errors are handled gracefully."""
        mock_collection.insert_one.side_effect = Exception("Connection failed")

        result = event_logger.log_question_asked(
            session_id="session_123",
            query="Test query",
        )

        assert result is None  # Should return None on error, not raise


class TestGetEventLogger:
    """Tests for the global event logger singleton."""

    def test_get_event_logger_returns_same_instance(self):
        """Test that get_event_logger returns the same instance."""
        with patch("chatbot.events._event_logger", None):
            logger1 = get_event_logger()
            logger2 = get_event_logger()
            assert logger1 is logger2
