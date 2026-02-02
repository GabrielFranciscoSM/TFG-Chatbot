"""
Professor dashboard endpoints.

This module provides endpoints for professors to manage their subjects,
view enrolled students, upload documents, and see usage statistics.
"""

from datetime import UTC, datetime, timedelta

import httpx
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from backend.config import settings
from backend.dependencies import (
    get_sessions_collection,
    get_users_collection,
    require_admin_or_professor,
)
from backend.models import UserInDB, UserRole
from backend.utils import get_test_user_filter

router = APIRouter(prefix="/professor", tags=["professor"])


# --- Response Models ---


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


# --- Endpoints ---


@router.get("/subjects", response_model=list[SubjectInfo])
async def list_professor_subjects(
    user: UserInDB = Depends(require_admin_or_professor),
    users_collection=Depends(get_users_collection),
):
    """
    List all subjects the professor teaches with student counts.

    For each subject, includes the number of enrolled students and documents.
    """
    subjects_info = []

    for subject in user.subjects:
        # Count students enrolled in this subject (excluding test users)
        student_count = users_collection.count_documents(
            {"role": UserRole.STUDENT, "subjects": subject, **get_test_user_filter()}
        )

        # Get document count from RAG service
        doc_count = 0
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{settings.rag_service_url}/files", params={"asignatura": subject}
                )
                if response.status_code == 200:
                    data = response.json()
                    doc_count = data.get("total_files", 0)
        except Exception:
            pass  # If RAG service is down, just show 0

        subjects_info.append(
            SubjectInfo(
                name=subject, student_count=student_count, document_count=doc_count
            )
        )

    return subjects_info


@router.get("/subjects/{subject}/students", response_model=list[StudentInfo])
async def list_subject_students(
    subject: str,
    user: UserInDB = Depends(require_admin_or_professor),
    users_collection=Depends(get_users_collection),
):
    """
    List all students enrolled in a specific subject.

    Only professors who teach this subject can view the student list.
    """
    # Verify professor teaches this subject
    if subject not in user.subjects:
        raise HTTPException(status_code=403, detail="You don't teach this subject")

    # Exclude test users from the list
    students = users_collection.find(
        {"role": UserRole.STUDENT, "subjects": subject, **get_test_user_filter()}
    )

    return [StudentInfo(username=s["username"], email=s["email"]) for s in students]


@router.get("/subjects/{subject}/documents", response_model=list[DocumentInfo])
async def list_subject_documents(
    subject: str,
    user: UserInDB = Depends(require_admin_or_professor),
):
    """
    List all documents for a specific subject from the RAG service.
    """
    # Verify professor teaches this subject
    if subject not in user.subjects:
        raise HTTPException(status_code=403, detail="You don't teach this subject")

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{settings.rag_service_url}/files", params={"asignatura": subject}
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail="Failed to fetch documents from RAG service",
            )

        data = response.json()
        documents = []

        for file_path in data.get("files", []):
            # Extract tipo_documento from path (subject/tipo/filename)
            parts = file_path.split("/")
            tipo = parts[1] if len(parts) > 2 else "unknown"
            filename = parts[-1]

            # Get file info
            try:
                info_response = await client.get(
                    f"{settings.rag_service_url}/files/{file_path}"
                )
                if info_response.status_code == 200:
                    info = info_response.json()
                    documents.append(
                        DocumentInfo(
                            filename=filename,
                            path=file_path,
                            size_kb=info.get("size_kb", 0),
                            tipo_documento=tipo,
                        )
                    )
            except Exception:
                # If we can't get info, still show the file
                documents.append(
                    DocumentInfo(
                        filename=filename,
                        path=file_path,
                        size_kb=0,
                        tipo_documento=tipo,
                    )
                )

        return documents


@router.post("/subjects/{subject}/documents")
async def upload_document(
    subject: str,
    file: UploadFile = File(...),
    tipo_documento: str = Form(default="teoria"),
    auto_index: bool = Form(default=True),
    user: UserInDB = Depends(require_admin_or_professor),
):
    """
    Upload a document for a specific subject.

    The document will be stored in the RAG service and optionally indexed
    for semantic search.
    """
    # Verify professor teaches this subject
    if subject not in user.subjects:
        raise HTTPException(status_code=403, detail="You don't teach this subject")

    # Prepare metadata with current date
    metadata = {
        "asignatura": subject,
        "tipo_documento": tipo_documento,
        "fecha": datetime.now(UTC).strftime("%Y-%m-%d"),
        "auto_index": auto_index,
        "autor": user.username,
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        # Read file content
        content = await file.read()

        # Send to RAG service
        files = {"file": (file.filename, content, file.content_type)}

        response = await client.post(
            f"{settings.rag_service_url}/upload",
            files=files,
            data={
                "metadata": str(metadata)
                .replace("'", '"')
                .replace("True", "true")
                .replace("False", "false")
            },
        )

        if response.status_code not in [200, 201]:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to upload document: {response.text}",
            )

        return response.json()


@router.delete("/subjects/{subject}/documents/{file_path:path}")
async def delete_document(
    subject: str,
    file_path: str,
    user: UserInDB = Depends(require_admin_or_professor),
):
    """
    Delete a document from a specific subject.

    This removes the file from the RAG service storage.
    """
    # Verify professor teaches this subject
    if subject not in user.subjects:
        raise HTTPException(status_code=403, detail="You don't teach this subject")

    # Verify the file belongs to this subject
    if not file_path.startswith(f"{subject}/"):
        raise HTTPException(
            status_code=403, detail="This document doesn't belong to your subject"
        )

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.delete(f"{settings.rag_service_url}/files/{file_path}")

        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Document not found")

        if response.status_code not in [200, 204]:
            raise HTTPException(
                status_code=response.status_code, detail="Failed to delete document"
            )

        return {"status": "deleted", "path": file_path}


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    user: UserInDB = Depends(require_admin_or_professor),
    users_collection=Depends(get_users_collection),
    sessions_collection=Depends(get_sessions_collection),
):
    """
    Get dashboard statistics for the professor.

    Includes:
    - Total students across all subjects
    - Total sessions in their subjects
    - Session activity over the last 7 days
    - Per-subject statistics
    """
    # Get unique students across all professor's subjects
    all_students = set()
    subject_stats = []
    total_documents = 0

    for subject in user.subjects:
        # Count students (excluding test users)
        students = list(
            users_collection.find(
                {
                    "role": UserRole.STUDENT,
                    "subjects": subject,
                    **get_test_user_filter(),
                }
            )
        )
        for s in students:
            all_students.add(s["username"])

        # Count sessions for this subject
        session_count = sessions_collection.count_documents({"subject": subject})

        # For now, message_count is approximated as session_count * 2 (1 user + 1 assistant per session minimum)
        # In a real implementation, you'd count actual messages
        message_count = session_count * 2

        subject_stats.append(
            SubjectStats(
                subject=subject,
                session_count=session_count,
                message_count=message_count,
            )
        )

        # Get document count
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{settings.rag_service_url}/files", params={"asignatura": subject}
                )
                if response.status_code == 200:
                    data = response.json()
                    total_documents += data.get("total_files", 0)
        except Exception:
            pass

    # Get total sessions
    total_sessions = sessions_collection.count_documents(
        {"subject": {"$in": user.subjects}}
    )

    # Get sessions per day for last 7 days
    sessions_last_7_days = []
    for i in range(7):
        day = datetime.now(UTC) - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)

        count = sessions_collection.count_documents(
            {
                "subject": {"$in": user.subjects},
                "created_at": {"$gte": day_start, "$lt": day_end},
            }
        )

        sessions_last_7_days.append(
            {"date": day_start.strftime("%Y-%m-%d"), "count": count}
        )

    # Reverse to show oldest first
    sessions_last_7_days.reverse()

    return DashboardStats(
        total_students=len(all_students),
        total_sessions=total_sessions,
        total_documents=total_documents,
        subjects=subject_stats,
        sessions_last_7_days=sessions_last_7_days,
    )


@router.get("/subjects/{subject}/progress", response_model=SubjectProgressResponse)
async def get_subject_progress(
    subject: str,
    user: UserInDB = Depends(require_admin_or_professor),
    users_collection=Depends(get_users_collection),
):
    """
    Get detailed learning progress for all students in a subject.

    Returns per-student metrics including:
    - Difficulty distribution (basic, intermediate, advanced questions)
    - Topic mastery levels within the subject
    - Test performance statistics
    - Recent activity timestamps

    This endpoint fetches student profiles from the chatbot service
    and aggregates them for the professor's dashboard view.
    """
    # Verify professor teaches this subject
    if subject not in user.subjects:
        raise HTTPException(status_code=403, detail="You don't teach this subject")

    # Get students enrolled in this subject (excluding test users)
    students = list(
        users_collection.find(
            {"role": UserRole.STUDENT, "subjects": subject, **get_test_user_filter()}
        )
    )
    student_usernames = [s["username"] for s in students]

    if not student_usernames:
        return SubjectProgressResponse(
            subject=subject,
            students=[],
            aggregated_stats=AggregatedStats(
                total_students=0,
                total_interactions=0,
                total_tests=0,
                difficulty_distribution={"basic": 0, "intermediate": 0, "advanced": 0},
            ),
        )

    # Get profiles from chatbot service (batch request)
    profiles_data: list[dict] = []
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.chatbot_service_url}/profiles/batch",
                json=student_usernames,
            )
            if response.status_code == 200:
                profiles_data = response.json()
    except Exception:
        pass  # If chatbot service is down, continue with empty profiles

    # Build profile lookup by user_id
    profiles_by_user = {p["user_id"]: p for p in profiles_data}

    # Build student progress list
    student_progress: list[StudentProgress] = []
    total_interactions = 0
    total_tests = 0
    all_difficulties: dict[str, int] = {"basic": 0, "intermediate": 0, "advanced": 0}

    for student in students:
        username = student["username"]
        profile = profiles_by_user.get(username, {})

        # Extract topics for this specific subject
        topics: list[TopicProgress] = []
        subject_mastery = profile.get("subject_mastery", {}).get(subject, {})
        for topic_name, mastery in subject_mastery.items():
            topics.append(
                TopicProgress(
                    topic=topic_name,
                    level=mastery.get("level", 0.5),
                    interactions_count=mastery.get("interactions_count", 0),
                    test_questions=mastery.get("total_test_questions", 0),
                    correct_answers=mastery.get("correct_answers", 0),
                )
            )

        # Get difficulty distribution
        diff_dist = profile.get(
            "difficulty_distribution",
            {"basic": 0, "intermediate": 0, "advanced": 0},
        )
        interactions = profile.get("total_interactions", 0)
        tests = profile.get("total_tests_taken", 0)

        # Aggregate stats across all students
        total_interactions += interactions
        total_tests += tests
        for k, v in diff_dist.items():
            if k in all_difficulties:
                all_difficulties[k] += v

        # Get last activity from recent_interactions
        recent = profile.get("recent_interactions", [])
        last_active = None
        if recent:
            last_ts = recent[-1].get("timestamp")
            if last_ts:
                # Handle both string and datetime formats
                if isinstance(last_ts, str):
                    try:
                        last_active = datetime.fromisoformat(
                            last_ts.replace("Z", "+00:00")
                        )
                    except ValueError:
                        pass
                else:
                    last_active = last_ts

        student_progress.append(
            StudentProgress(
                username=username,
                email=student["email"],
                total_interactions=interactions,
                difficulty_distribution=diff_dist,
                topics=topics,
                tests_taken=tests,
                average_test_score=profile.get("average_test_score"),
                last_active=last_active,
            )
        )

    # Sort by total interactions (most active students first)
    student_progress.sort(key=lambda s: s.total_interactions, reverse=True)

    return SubjectProgressResponse(
        subject=subject,
        students=student_progress,
        aggregated_stats=AggregatedStats(
            total_students=len(students),
            total_interactions=total_interactions,
            total_tests=total_tests,
            difficulty_distribution=all_difficulties,
        ),
    )
