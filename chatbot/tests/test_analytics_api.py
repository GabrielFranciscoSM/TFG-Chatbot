"""
Tests for the Analytics API endpoints in chatbot service.

Tests the /profiles/batch and /conversations/stats endpoints.
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from chatbot.api import app


@pytest.fixture
def api_client():
    """Create a test client for the chatbot API."""
    return TestClient(app)


@pytest.fixture
def mock_profile_manager():
    """Create a mock ProfileManager."""
    manager = MagicMock()
    return manager


@pytest.mark.unit
class TestProfilesBatchEndpoint:
    """Tests for POST /profiles/batch endpoint."""

    def test_batch_empty_list(self, api_client):
        """Test with empty user list."""
        with patch("chatbot.api.get_profile_manager") as mock_get_pm:
            mock_pm = MagicMock()
            mock_get_pm.return_value = mock_pm

            response = api_client.post("/profiles/batch", json=[])

            assert response.status_code == 200
            assert response.json() == []

    def test_batch_single_user_found(self, api_client):
        """Test with a single user that has a profile."""
        mock_profile = MagicMock()
        mock_profile.model_dump.return_value = {
            "user_id": "student1",
            "total_interactions": 10,
            "difficulty_distribution": {"basic": 5, "intermediate": 3, "advanced": 2},
        }

        with patch("chatbot.api.get_profile_manager") as mock_get_pm:
            mock_pm = MagicMock()
            mock_pm.get_profile.return_value = mock_profile
            mock_get_pm.return_value = mock_pm

            response = api_client.post("/profiles/batch", json=["student1"])

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["user_id"] == "student1"

    def test_batch_user_not_found(self, api_client):
        """Test with a user that has no profile."""
        with patch("chatbot.api.get_profile_manager") as mock_get_pm:
            mock_pm = MagicMock()
            mock_pm.get_profile.return_value = None
            mock_get_pm.return_value = mock_pm

            response = api_client.post("/profiles/batch", json=["nonexistent"])

            assert response.status_code == 200
            assert response.json() == []

    def test_batch_mixed_users(self, api_client):
        """Test with some users found, some not."""
        mock_profile1 = MagicMock()
        mock_profile1.model_dump.return_value = {"user_id": "student1"}

        mock_profile3 = MagicMock()
        mock_profile3.model_dump.return_value = {"user_id": "student3"}

        with patch("chatbot.api.get_profile_manager") as mock_get_pm:
            mock_pm = MagicMock()

            # student1 found, student2 not found, student3 found
            def get_profile_side_effect(user_id):
                if user_id == "student1":
                    return mock_profile1
                elif user_id == "student3":
                    return mock_profile3
                return None

            mock_pm.get_profile.side_effect = get_profile_side_effect
            mock_get_pm.return_value = mock_pm

            response = api_client.post(
                "/profiles/batch", json=["student1", "student2", "student3"]
            )

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            user_ids = [d["user_id"] for d in data]
            assert "student1" in user_ids
            assert "student3" in user_ids
            assert "student2" not in user_ids


@pytest.mark.unit
class TestConversationStatsEndpoint:
    """Tests for GET /conversations/stats endpoint."""

    def test_stats_no_filters(self, api_client):
        """Test stats without any filters."""
        mock_collection = MagicMock()
        mock_collection.aggregate.return_value = [
            {
                "_id": None,
                "total_conversations": 100,
                "unique_users": ["user1", "user2", "user3"],
                "unique_sessions": ["sess1", "sess2"],
                "difficulty_counts": ["basic", "basic", "intermediate", "advanced"],
                "avg_latency_ms": 250.5,
                "test_conversations": 10,
            }
        ]

        with patch("chatbot.api.get_profile_manager") as mock_get_pm:
            mock_pm = MagicMock()
            mock_pm.db_client.get_collection.return_value = mock_collection
            mock_pm.CONVERSATIONS_COLLECTION = "conversations"
            mock_get_pm.return_value = mock_pm

            response = api_client.get("/conversations/stats")

            assert response.status_code == 200
            data = response.json()
            assert data["total_conversations"] == 100
            assert data["unique_users"] == 3
            assert data["unique_sessions"] == 2
            assert data["difficulty_distribution"]["basic"] == 2
            assert data["difficulty_distribution"]["intermediate"] == 1
            assert data["avg_latency_ms"] == 250.5
            assert data["test_conversations"] == 10

    def test_stats_with_user_filter(self, api_client):
        """Test stats filtered by user IDs."""
        mock_collection = MagicMock()
        mock_collection.aggregate.return_value = [
            {
                "_id": None,
                "total_conversations": 25,
                "unique_users": ["user1"],
                "unique_sessions": ["sess1"],
                "difficulty_counts": ["basic", "intermediate"],
                "avg_latency_ms": 200.0,
                "test_conversations": 5,
            }
        ]

        with patch("chatbot.api.get_profile_manager") as mock_get_pm:
            mock_pm = MagicMock()
            mock_pm.db_client.get_collection.return_value = mock_collection
            mock_pm.CONVERSATIONS_COLLECTION = "conversations"
            mock_get_pm.return_value = mock_pm

            response = api_client.get("/conversations/stats?user_ids=user1,user2")

            assert response.status_code == 200
            # Verify the aggregation was called with proper filter
            call_args = mock_collection.aggregate.call_args[0][0]
            match_stage = call_args[0]
            assert "$match" in match_stage
            assert "user_id" in match_stage["$match"]
            assert match_stage["$match"]["user_id"] == {"$in": ["user1", "user2"]}

    def test_stats_with_subject_filter(self, api_client):
        """Test stats filtered by subject."""
        mock_collection = MagicMock()
        mock_collection.aggregate.return_value = [
            {
                "_id": None,
                "total_conversations": 50,
                "unique_users": ["user1", "user2"],
                "unique_sessions": ["sess1"],
                "difficulty_counts": ["intermediate"],
                "avg_latency_ms": 300.0,
                "test_conversations": 3,
            }
        ]

        with patch("chatbot.api.get_profile_manager") as mock_get_pm:
            mock_pm = MagicMock()
            mock_pm.db_client.get_collection.return_value = mock_collection
            mock_pm.CONVERSATIONS_COLLECTION = "conversations"
            mock_get_pm.return_value = mock_pm

            response = api_client.get("/conversations/stats?subject=iv")

            assert response.status_code == 200
            # Verify the aggregation was called with subject filter
            call_args = mock_collection.aggregate.call_args[0][0]
            match_stage = call_args[0]
            assert match_stage["$match"]["subject"] == "iv"

    def test_stats_empty_result(self, api_client):
        """Test stats when no conversations exist."""
        mock_collection = MagicMock()
        mock_collection.aggregate.return_value = []

        with patch("chatbot.api.get_profile_manager") as mock_get_pm:
            mock_pm = MagicMock()
            mock_pm.db_client.get_collection.return_value = mock_collection
            mock_pm.CONVERSATIONS_COLLECTION = "conversations"
            mock_get_pm.return_value = mock_pm

            response = api_client.get("/conversations/stats")

            assert response.status_code == 200
            data = response.json()
            assert data["total_conversations"] == 0
            assert data["unique_users"] == 0
            assert data["unique_sessions"] == 0
            assert data["difficulty_distribution"] == {}
            assert data["avg_latency_ms"] is None
            assert data["test_conversations"] == 0
