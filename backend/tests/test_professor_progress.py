"""
Tests for professor progress dashboard endpoint.

Tests the GET /professor/subjects/{subject}/progress endpoint
which returns detailed learning progress for students in a subject.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.models import UserRole


@pytest.mark.unit
class TestSubjectProgress:
    """Tests for the subject progress endpoint."""

    def test_get_progress_unauthorized(self, client):
        """Test that unauthenticated requests are rejected."""
        response = client.get("/professor/subjects/iv/progress")
        assert response.status_code == 401

    def test_get_progress_student_forbidden(self, client, student_token):
        """Test that students cannot access progress endpoint."""
        response = client.get(
            "/professor/subjects/iv/progress",
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert response.status_code == 403

    def test_get_progress_wrong_subject(self, client, professor_token, test_professor):
        """Test that professors can only view subjects they teach."""
        response = client.get(
            "/professor/subjects/unknown-subject/progress",
            headers={"Authorization": f"Bearer {professor_token}"},
        )
        assert response.status_code == 403
        assert "don't teach" in response.json()["detail"]

    def test_get_progress_no_students(self, client, professor_token, test_professor):
        """Test progress endpoint with no enrolled students."""
        response = client.get(
            "/professor/subjects/iv/progress",
            headers={"Authorization": f"Bearer {professor_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["subject"] == "iv"
        assert data["students"] == []
        assert data["aggregated_stats"]["total_students"] == 0

    def test_get_progress_with_students(
        self, client, professor_token, test_professor, mock_users_collection
    ):
        """Test progress endpoint with enrolled students."""
        # Create test students enrolled in 'iv'
        mock_users_collection.insert_many(
            [
                {
                    "username": "student_a",
                    "email": "a@test.com",
                    "role": UserRole.STUDENT,
                    "subjects": ["iv"],
                },
                {
                    "username": "student_b",
                    "email": "b@test.com",
                    "role": UserRole.STUDENT,
                    "subjects": ["iv", "dsd"],
                },
            ]
        )

        # Mock the chatbot service response
        mock_profiles = [
            {
                "user_id": "student_a",
                "total_interactions": 15,
                "total_tests_taken": 2,
                "average_test_score": 0.8,
                "difficulty_distribution": {
                    "basic": 5,
                    "intermediate": 7,
                    "advanced": 3,
                },
                "subject_mastery": {
                    "iv": {
                        "docker": {
                            "level": 0.7,
                            "interactions_count": 5,
                            "total_test_questions": 3,
                            "correct_answers": 2,
                        }
                    }
                },
                "recent_interactions": [
                    {"timestamp": "2026-02-13T10:00:00Z", "query": "test"}
                ],
            },
            {
                "user_id": "student_b",
                "total_interactions": 8,
                "total_tests_taken": 1,
                "average_test_score": 0.6,
                "difficulty_distribution": {
                    "basic": 4,
                    "intermediate": 3,
                    "advanced": 1,
                },
                "subject_mastery": {},
                "recent_interactions": [],
            },
        ]

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_profiles

            mock_client_instance = AsyncMock()
            mock_client_instance.post = AsyncMock(return_value=mock_response)
            mock_client_instance.__aenter__ = AsyncMock(
                return_value=mock_client_instance
            )
            mock_client_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_client_instance

            response = client.get(
                "/professor/subjects/iv/progress",
                headers={"Authorization": f"Bearer {professor_token}"},
            )

        assert response.status_code == 200
        data = response.json()

        # Check subject
        assert data["subject"] == "iv"

        # Check students are returned
        assert len(data["students"]) == 2

        # Students should be sorted by interactions (most active first)
        assert data["students"][0]["username"] == "student_a"
        assert data["students"][0]["total_interactions"] == 15
        assert data["students"][0]["tests_taken"] == 2
        assert data["students"][0]["average_test_score"] == 0.8

        # Check topics for student_a
        topics = data["students"][0]["topics"]
        assert len(topics) == 1
        assert topics[0]["topic"] == "docker"
        assert topics[0]["level"] == 0.7

        # Check aggregated stats
        stats = data["aggregated_stats"]
        assert stats["total_students"] == 2
        assert stats["total_interactions"] == 23  # 15 + 8
        assert stats["total_tests"] == 3  # 2 + 1
        assert stats["difficulty_distribution"]["basic"] == 9  # 5 + 4
        assert stats["difficulty_distribution"]["intermediate"] == 10  # 7 + 3

    def test_get_progress_chatbot_service_down(
        self, client, professor_token, test_professor, mock_users_collection
    ):
        """Test graceful handling when chatbot service is unavailable."""
        # Create a student
        mock_users_collection.insert_one(
            {
                "username": "student_c",
                "email": "c@test.com",
                "role": UserRole.STUDENT,
                "subjects": ["iv"],
            }
        )

        # Mock chatbot service being down
        with patch("httpx.AsyncClient") as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.post = AsyncMock(
                side_effect=Exception("Connection refused")
            )
            mock_client_instance.__aenter__ = AsyncMock(
                return_value=mock_client_instance
            )
            mock_client_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_client_instance

            response = client.get(
                "/professor/subjects/iv/progress",
                headers={"Authorization": f"Bearer {professor_token}"},
            )

        # Should still return 200 with empty profiles
        assert response.status_code == 200
        data = response.json()
        assert len(data["students"]) == 1
        assert data["students"][0]["username"] == "student_c"
        assert data["students"][0]["total_interactions"] == 0
        assert data["students"][0]["topics"] == []
