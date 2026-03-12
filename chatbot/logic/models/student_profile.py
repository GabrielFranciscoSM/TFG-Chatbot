"""
Student Knowledge Profile Models.

Pydantic models for tracking student learning progress and interactions
to enable adaptive responses based on demonstrated knowledge level.

Schema designed for MongoDB persistence with efficient querying and updates.
"""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class Interaction(BaseModel):
    """Record of a single learning interaction.

    Captures the essential data from each chat exchange to build
    a picture of the student's engagement and knowledge level.
    """

    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    query: str = Field(..., description="User's question or input")
    difficulty: str = Field(
        default="unknown",
        description="Classified difficulty: basic, intermediate, advanced, unknown",
    )
    topic: str | None = Field(None, description="Extracted topic from query/response")
    subject: str | None = Field(None, description="Subject/course context (asignatura)")
    was_test: bool = Field(default=False, description="Whether this was a test session")
    test_score: float | None = Field(
        None, ge=0.0, le=1.0, description="Test score as ratio (0-1) if applicable"
    )


class TopicMastery(BaseModel):
    """Mastery level for a specific topic within a subject.

    Tracks cumulative understanding based on interaction history
    and test performance.
    """

    level: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Mastery level from 0 (novice) to 1 (expert)",
    )
    interactions_count: int = Field(
        default=0, description="Number of interactions on this topic"
    )
    correct_answers: int = Field(
        default=0, description="Correct test answers on this topic"
    )
    total_test_questions: int = Field(
        default=0, description="Total test questions attempted on this topic"
    )
    last_interaction: datetime | None = Field(
        None, description="Timestamp of most recent interaction"
    )


class StudentProfile(BaseModel):
    """Complete student knowledge profile for adaptive learning.

    Aggregates interaction history to determine appropriate response
    difficulty and track learning progress over time.

    MongoDB document structure:
        - _id: user_id (unique per student)
        - Flat structure for efficient partial updates
        - subject_mastery uses nested dicts: {subject: {topic: TopicMastery}}
    """

    user_id: str = Field(..., description="Unique user identifier")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Aggregated metrics
    total_interactions: int = Field(default=0, description="Total chat interactions")
    difficulty_distribution: dict[str, int] = Field(
        default_factory=lambda: {"basic": 0, "intermediate": 0, "advanced": 0},
        description="Count of queries by difficulty level",
    )

    # Per-subject, per-topic mastery tracking
    # Structure: {subject_id: {topic_name: TopicMastery}}
    subject_mastery: dict[str, dict[str, dict[str, Any]]] = Field(
        default_factory=dict,
        description="Mastery levels organized by subject and topic",
    )

    # Recent interactions for context (capped to avoid unbounded growth)
    recent_interactions: list[Interaction] = Field(
        default_factory=list,
        description="Last N interactions for quick context lookup",
    )

    # Test session performance
    total_tests_taken: int = Field(default=0, description="Number of completed tests")
    average_test_score: float | None = Field(
        None, ge=0.0, le=1.0, description="Running average of test scores"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "student123",
                "created_at": "2026-02-12T10:00:00Z",
                "updated_at": "2026-02-12T15:30:00Z",
                "total_interactions": 25,
                "difficulty_distribution": {
                    "basic": 10,
                    "intermediate": 12,
                    "advanced": 3,
                },
                "subject_mastery": {
                    "iv": {
                        "docker": {
                            "level": 0.75,
                            "interactions_count": 5,
                            "correct_answers": 3,
                            "total_test_questions": 4,
                            "last_interaction": "2026-02-12T15:30:00Z",
                        }
                    }
                },
                "recent_interactions": [
                    {
                        "timestamp": "2026-02-12T15:30:00Z",
                        "query": "¿Qué es Docker Compose?",
                        "difficulty": "intermediate",
                        "topic": "docker",
                        "subject": "iv",
                        "was_test": False,
                        "test_score": None,
                    }
                ],
                "total_tests_taken": 3,
                "average_test_score": 0.8,
            }
        }
    }


class ConversationTurn(BaseModel):
    """A single conversation turn (question + answer pair) for persistence.

    Stored in the 'conversations' collection for full conversation
    history analysis and research purposes.
    """

    session_id: str = Field(..., description="Chat session identifier")
    user_id: str | None = Field(None, description="User identifier if known")
    subject: str | None = Field(None, description="Subject context")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Full content (not truncated)
    query: str = Field(..., description="User's question")
    answer: str = Field(..., description="Full chatbot response")

    # Metadata for analysis
    difficulty: str | None = Field(None, description="Classified difficulty level")
    latency_ms: float | None = Field(None, description="Response time in milliseconds")
    rag_sources_used: list[str] | None = Field(
        None, description="RAG document sources consulted"
    )
    was_test: bool = Field(default=False, description="Whether part of test session")

    model_config = {
        "json_schema_extra": {
            "example": {
                "session_id": "session-abc-123",
                "user_id": "student456",
                "subject": "iv",
                "timestamp": "2026-02-12T15:30:00Z",
                "query": "¿Qué es integración continua?",
                "answer": "La integración continua (CI) es una práctica de desarrollo...",
                "difficulty": "intermediate",
                "latency_ms": 1250.5,
                "rag_sources_used": ["ci_cd_docs.md", "devops_guide.pdf"],
                "was_test": False,
            }
        }
    }
