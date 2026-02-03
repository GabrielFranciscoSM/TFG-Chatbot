from datetime import datetime

from pydantic import BaseModel


class StudentInfo(BaseModel):
    username: str
    email: str


class SubjectInfo(BaseModel):
    name: str
    student_count: int
    document_count: int


class SubjectDetail(BaseModel):
    name: str
    students: list[StudentInfo]
    document_count: int


class DocumentInfo(BaseModel):
    filename: str
    path: str
    size_kb: float
    tipo_documento: str


class SubjectStats(BaseModel):
    subject: str
    session_count: int
    message_count: int


class DashboardStats(BaseModel):
    total_students: int
    total_sessions: int
    total_documents: int
    subjects: list[SubjectStats]
    sessions_last_7_days: list[dict]


# --- Progress Dashboard Models ---


class TopicProgress(BaseModel):
    """Progress metrics for a specific topic."""

    topic: str
    level: float  # 0-1 mastery level
    interactions_count: int
    test_questions: int
    correct_answers: int


class StudentProgress(BaseModel):
    """Detailed learning progress for a student."""

    username: str
    email: str
    total_interactions: int
    difficulty_distribution: dict[str, int]
    topics: list[TopicProgress]
    tests_taken: int
    average_test_score: float | None
    last_active: datetime | None


class AggregatedStats(BaseModel):
    """Aggregated statistics for a subject."""

    total_students: int
    total_interactions: int
    total_tests: int
    difficulty_distribution: dict[str, int]


class SubjectProgressResponse(BaseModel):
    """Response model for subject progress endpoint."""

    subject: str
    students: list[StudentProgress]
    aggregated_stats: AggregatedStats
