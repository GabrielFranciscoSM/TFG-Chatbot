"""
Tests for the ProfileManager module.

These tests verify that the ProfileManager correctly manages student
knowledge profiles and conversation persistence in MongoDB.
"""

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

from chatbot.logic.models.student_profile import (
    ConversationTurn,
    Interaction,
    StudentProfile,
)
from chatbot.logic.profile_manager import ProfileManager, get_profile_manager


class TestProfileManager:
    """Tests for the ProfileManager class."""

    @pytest.fixture
    def mock_collection(self):
        """Create a mock MongoDB collection."""
        collection = MagicMock()
        collection.insert_one.return_value = MagicMock(inserted_id="test_profile_id")
        collection.update_one.return_value = MagicMock(
            modified_count=1, upserted_id=None
        )
        collection.find_one.return_value = None
        return collection

    @pytest.fixture
    def mock_db_client(self, mock_collection):
        """Create a mock MongoDB client."""
        client = MagicMock()
        client.get_collection.return_value = mock_collection
        return client

    @pytest.fixture
    def profile_manager(self, mock_db_client):
        """Create a ProfileManager with mocked database."""
        return ProfileManager(db_client=mock_db_client)

    # --- Profile CRUD Tests ---

    def test_get_profile_not_found(self, profile_manager, mock_collection):
        """Test getting a profile that doesn't exist."""
        mock_collection.find_one.return_value = None

        result = profile_manager.get_profile("nonexistent_user")

        assert result is None
        mock_collection.find_one.assert_called_once_with({"_id": "nonexistent_user"})

    def test_get_profile_found(self, profile_manager, mock_collection):
        """Test getting an existing profile."""
        mock_collection.find_one.return_value = {
            "_id": "user123",
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
            "total_interactions": 10,
            "difficulty_distribution": {"basic": 5, "intermediate": 3, "advanced": 2},
            "subject_mastery": {},
            "recent_interactions": [],
            "total_tests_taken": 0,
            "average_test_score": None,
        }

        result = profile_manager.get_profile("user123")

        assert result is not None
        assert result.user_id == "user123"
        assert result.total_interactions == 10

    def test_get_or_create_profile_existing(self, profile_manager, mock_collection):
        """Test get_or_create returns existing profile."""
        mock_collection.find_one.return_value = {
            "_id": "user123",
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
            "total_interactions": 5,
            "difficulty_distribution": {"basic": 0, "intermediate": 0, "advanced": 0},
            "subject_mastery": {},
            "recent_interactions": [],
            "total_tests_taken": 0,
            "average_test_score": None,
        }

        result = profile_manager.get_or_create_profile("user123")

        assert result.user_id == "user123"
        assert result.total_interactions == 5
        # Should not have called insert_one since profile exists
        mock_collection.insert_one.assert_not_called()

    def test_get_or_create_profile_new(self, profile_manager, mock_collection):
        """Test get_or_create creates new profile when none exists."""
        mock_collection.find_one.return_value = None

        result = profile_manager.get_or_create_profile("new_user")

        assert result.user_id == "new_user"
        assert result.total_interactions == 0
        mock_collection.insert_one.assert_called_once()

        # Verify the document structure
        call_args = mock_collection.insert_one.call_args[0][0]
        assert call_args["_id"] == "new_user"
        assert "created_at" in call_args
        assert "updated_at" in call_args

    # --- Interaction Recording Tests ---

    def test_record_interaction_basic(self, profile_manager, mock_collection):
        """Test recording a basic interaction."""
        result = profile_manager.record_interaction(
            user_id="user123",
            query="¿Qué es Docker?",
            difficulty="intermediate",
            subject="iv",
            topic="docker",
        )

        assert result is True
        mock_collection.update_one.assert_called_once()

        # Verify the update operations
        call_args = mock_collection.update_one.call_args
        filter_query = call_args[0][0]
        update_ops = call_args[0][1]

        assert filter_query == {"_id": "user123"}
        assert "$set" in update_ops
        assert "$inc" in update_ops
        assert "$push" in update_ops

        # Check increments
        assert update_ops["$inc"]["total_interactions"] == 1
        assert update_ops["$inc"]["difficulty_distribution.intermediate"] == 1
        assert update_ops["$inc"]["subject_mastery.iv.docker.interactions_count"] == 1

    def test_record_interaction_updates_difficulty_distribution(
        self, profile_manager, mock_collection
    ):
        """Test that difficulty distribution is updated correctly."""
        profile_manager.record_interaction(
            user_id="user123",
            query="Simple question",
            difficulty="basic",
        )

        call_args = mock_collection.update_one.call_args[0][1]
        assert call_args["$inc"]["difficulty_distribution.basic"] == 1

    def test_record_interaction_with_test_score(self, profile_manager, mock_collection):
        """Test recording an interaction that was part of a test."""
        # Mock find_one for average calculation
        mock_collection.find_one.return_value = {
            "total_tests_taken": 1,
            "average_test_score": 0.8,
        }

        result = profile_manager.record_interaction(
            user_id="user123",
            query="Test question",
            difficulty="advanced",
            was_test=True,
            test_score=0.75,
        )

        assert result is True

        # Should have incremented total_tests_taken
        call_args = mock_collection.update_one.call_args_list[0][0][1]
        assert call_args["$inc"]["total_tests_taken"] == 1

    def test_record_interaction_unknown_difficulty(
        self, profile_manager, mock_collection
    ):
        """Test that unknown difficulty doesn't increment distribution."""
        profile_manager.record_interaction(
            user_id="user123",
            query="Some question",
            difficulty="unknown",
        )

        call_args = mock_collection.update_one.call_args[0][1]
        # Should not have any difficulty_distribution increment
        assert "difficulty_distribution.unknown" not in call_args.get("$inc", {})

    # --- Topic Mastery Tests ---

    def test_update_topic_mastery_correct_answer(
        self, profile_manager, mock_collection
    ):
        """Test mastery increases on correct answer."""
        mock_collection.find_one.return_value = {
            "subject_mastery": {"iv": {"docker": {"level": 0.5}}}
        }

        result = profile_manager.update_topic_mastery(
            user_id="user123",
            subject="iv",
            topic="docker",
            correct=True,
        )

        assert result is True

        call_args = mock_collection.update_one.call_args[0][1]
        # Level should be updated (0.5 + 0.1 = 0.6)
        assert call_args["$set"]["subject_mastery.iv.docker.level"] == 0.6
        assert call_args["$inc"]["subject_mastery.iv.docker.correct_answers"] == 1

    def test_update_topic_mastery_incorrect_answer(
        self, profile_manager, mock_collection
    ):
        """Test mastery decreases on incorrect answer."""
        mock_collection.find_one.return_value = {
            "subject_mastery": {"iv": {"docker": {"level": 0.5}}}
        }

        result = profile_manager.update_topic_mastery(
            user_id="user123",
            subject="iv",
            topic="docker",
            correct=False,
        )

        assert result is True

        call_args = mock_collection.update_one.call_args[0][1]
        # Level should be updated (0.5 - 0.05 = 0.45)
        assert call_args["$set"]["subject_mastery.iv.docker.level"] == 0.45
        # correct_answers should NOT be incremented
        assert "subject_mastery.iv.docker.correct_answers" not in call_args.get(
            "$inc", {}
        )

    def test_update_topic_mastery_bounds(self, profile_manager, mock_collection):
        """Test mastery stays within 0-1 bounds."""
        # Test upper bound
        mock_collection.find_one.return_value = {
            "subject_mastery": {"iv": {"docker": {"level": 0.95}}}
        }

        profile_manager.update_topic_mastery(
            user_id="user123", subject="iv", topic="docker", correct=True
        )

        call_args = mock_collection.update_one.call_args[0][1]
        assert call_args["$set"]["subject_mastery.iv.docker.level"] == 1.0

        # Test lower bound
        mock_collection.find_one.return_value = {
            "subject_mastery": {"iv": {"docker": {"level": 0.02}}}
        }

        profile_manager.update_topic_mastery(
            user_id="user123", subject="iv", topic="docker", correct=False
        )

        call_args = mock_collection.update_one.call_args[0][1]
        assert call_args["$set"]["subject_mastery.iv.docker.level"] == 0.0

    # --- Conversation Turn Tests ---

    def test_save_conversation_turn(self, profile_manager, mock_collection):
        """Test saving a full conversation turn."""
        result = profile_manager.save_conversation_turn(
            session_id="session123",
            query="¿Qué es integración continua?",
            answer="La integración continua (CI) es una práctica...",
            user_id="user123",
            subject="iv",
            difficulty="intermediate",
            latency_ms=1250.5,
            rag_sources_used=["ci_docs.md", "devops_guide.pdf"],
        )

        assert result == "test_profile_id"
        mock_collection.insert_one.assert_called_once()

        call_args = mock_collection.insert_one.call_args[0][0]
        assert call_args["session_id"] == "session123"
        assert call_args["user_id"] == "user123"
        assert call_args["query"] == "¿Qué es integración continua?"
        assert "La integración continua" in call_args["answer"]
        assert call_args["difficulty"] == "intermediate"
        assert call_args["latency_ms"] == 1250.5
        assert call_args["rag_sources_used"] == ["ci_docs.md", "devops_guide.pdf"]
        assert call_args["was_test"] is False

    def test_save_conversation_turn_test_session(
        self, profile_manager, mock_collection
    ):
        """Test saving a conversation turn from a test session."""
        profile_manager.save_conversation_turn(
            session_id="session123",
            query="Test question",
            answer="Your answer was correct!",
            was_test=True,
        )

        call_args = mock_collection.insert_one.call_args[0][0]
        assert call_args["was_test"] is True

    def test_get_conversation_history(self, profile_manager, mock_collection):
        """Test retrieving conversation history."""
        mock_collection.find.return_value.sort.return_value.limit.return_value = [
            {
                "session_id": "session123",
                "user_id": "user123",
                "subject": "iv",
                "timestamp": datetime.now(UTC),
                "query": "Question 1",
                "answer": "Answer 1",
                "difficulty": "basic",
                "latency_ms": 1000,
                "rag_sources_used": None,
                "was_test": False,
            }
        ]

        result = profile_manager.get_conversation_history(
            session_id="session123", user_id="user123", limit=50
        )

        assert len(result) == 1
        assert result[0].query == "Question 1"
        assert result[0].answer == "Answer 1"

        # Verify query parameters
        mock_collection.find.assert_called_once()
        query = mock_collection.find.call_args[0][0]
        assert query["session_id"] == "session123"
        assert query["user_id"] == "user123"


class TestProfileManagerGlobal:
    """Tests for global ProfileManager instance."""

    def test_get_profile_manager_singleton(self):
        """Test that get_profile_manager returns consistent instance."""
        # Reset global state
        import chatbot.logic.profile_manager as pm

        pm._profile_manager = None

        with patch.object(ProfileManager, "__init__", return_value=None):
            manager1 = get_profile_manager()
            manager2 = get_profile_manager()
            assert manager1 is manager2


class TestStudentProfileModel:
    """Tests for the StudentProfile Pydantic model."""

    def test_default_values(self):
        """Test that StudentProfile has correct defaults."""
        profile = StudentProfile(user_id="test_user")

        assert profile.user_id == "test_user"
        assert profile.total_interactions == 0
        assert profile.difficulty_distribution == {
            "basic": 0,
            "intermediate": 0,
            "advanced": 0,
        }
        assert profile.subject_mastery == {}
        assert profile.recent_interactions == []
        assert profile.total_tests_taken == 0
        assert profile.average_test_score is None

    def test_interaction_model(self):
        """Test the Interaction model."""
        interaction = Interaction(
            query="Test query",
            difficulty="intermediate",
            topic="docker",
            subject="iv",
        )

        assert interaction.query == "Test query"
        assert interaction.difficulty == "intermediate"
        assert interaction.was_test is False
        assert interaction.test_score is None

    def test_conversation_turn_model(self):
        """Test the ConversationTurn model."""
        turn = ConversationTurn(
            session_id="session123",
            query="Test query",
            answer="Test answer",
            user_id="user123",
            difficulty="basic",
        )

        assert turn.session_id == "session123"
        assert turn.query == "Test query"
        assert turn.answer == "Test answer"
        assert turn.was_test is False
