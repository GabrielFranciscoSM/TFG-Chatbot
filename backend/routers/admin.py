from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.dependencies import (
    get_sessions_collection,
    get_subjects_collection,
    get_users_collection,
    require_admin_or_professor,
)
from backend.models import AdminEnrollmentRequest, UserInDB, UserRole

router = APIRouter(prefix="/admin", tags=["admin"])


# --- Request/Response Models ---


class AssignSubjectRequest(BaseModel):
    username: str
    subject: str


class BatchEnrollmentRequest(BaseModel):
    usernames: list[str]
    subject: str


class PromoteUserRequest(BaseModel):
    username: str
    new_role: UserRole


class UserInfo(BaseModel):
    username: str
    email: str
    role: UserRole
    subjects: list[str]


class AdminStats(BaseModel):
    total_students: int
    total_professors: int
    total_admins: int
    total_sessions: int
    total_subjects: int
    sessions_last_7_days: list[dict]


# --- Helper to check admin only ---


def require_admin(user: UserInDB):
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")


# --- Endpoints ---


@router.get("/stats", response_model=AdminStats)
async def get_admin_stats(
    user: UserInDB = Depends(require_admin_or_professor),
    users_collection=Depends(get_users_collection),
    sessions_collection=Depends(get_sessions_collection),
):
    """
    Get global system statistics. Admin only.
    """
    require_admin(user)

    # Count users by role
    total_students = users_collection.count_documents({"role": UserRole.STUDENT})
    total_professors = users_collection.count_documents({"role": UserRole.PROFESSOR})
    total_admins = users_collection.count_documents({"role": UserRole.ADMIN})

    # Count total sessions
    total_sessions = sessions_collection.count_documents({})

    # Get unique subjects
    all_subjects = set()
    for u in users_collection.find({"subjects": {"$exists": True, "$ne": []}}):
        all_subjects.update(u.get("subjects", []))

    # Sessions in last 7 days
    sessions_by_day = []

    for i in range(7):
        day = datetime.now(UTC) - timedelta(days=6 - i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)

        count = sessions_collection.count_documents(
            {"created_at": {"$gte": day_start, "$lt": day_end}}
        )
        sessions_by_day.append({"date": day_start.strftime("%Y-%m-%d"), "count": count})

    return AdminStats(
        total_students=total_students,
        total_professors=total_professors,
        total_admins=total_admins,
        total_sessions=total_sessions,
        total_subjects=len(all_subjects),
        sessions_last_7_days=sessions_by_day,
    )


@router.get("/users", response_model=list[UserInfo])
async def list_users(
    role: UserRole | None = None,
    user: UserInDB = Depends(require_admin_or_professor),
    users_collection=Depends(get_users_collection),
):
    """
    List all users. Admin only. Optionally filter by role.
    """
    require_admin(user)

    query = {}
    if role:
        query["role"] = role

    users = users_collection.find(query)
    return [
        UserInfo(
            username=u["username"],
            email=u["email"],
            role=u.get("role", UserRole.STUDENT),
            subjects=u.get("subjects", []),
        )
        for u in users
    ]


@router.get("/users/search", response_model=list[UserInfo])
async def search_users(
    q: str,
    role: UserRole | None = None,
    limit: int = 10,
    user: UserInDB = Depends(require_admin_or_professor),
    users_collection=Depends(get_users_collection),
):
    """
    Search users by username prefix. For autocomplete functionality.
    - Professors can search students only.
    - Admins can search all users.
    """
    if len(q) < 2:
        return []

    query: dict = {"username": {"$regex": f"^{q}", "$options": "i"}}

    # Professors can only search students
    if user.role == UserRole.PROFESSOR:
        query["role"] = UserRole.STUDENT
    elif role:
        query["role"] = role

    users = users_collection.find(query).limit(limit)
    return [
        UserInfo(
            username=u["username"],
            email=u["email"],
            role=u.get("role", UserRole.STUDENT),
            subjects=u.get("subjects", []),
        )
        for u in users
    ]


@router.post("/enroll")
async def admin_enroll(
    request: AdminEnrollmentRequest,
    user: UserInDB = Depends(require_admin_or_professor),
    users_collection=Depends(get_users_collection),
    subjects_collection=Depends(get_subjects_collection),
):
    """
    Enroll a student in a subject.
    - Professors can only enroll students in their own subjects.
    - Admins can enroll anyone in any subject.
    """
    # Validate subject exists
    subject_doc = subjects_collection.find_one({"name": request.subject})
    if not subject_doc:
        raise HTTPException(
            status_code=404, detail="Subject not found. Create it first."
        )

    # Find target user
    target_user = users_collection.find_one({"username": request.username})
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Only students can be enrolled
    if target_user.get("role", UserRole.STUDENT) != UserRole.STUDENT:
        raise HTTPException(
            status_code=400, detail="Only students can be enrolled in subjects"
        )

    # Professors can only enroll in their own subjects
    if user.role == UserRole.PROFESSOR:
        if request.subject not in user.subjects:
            raise HTTPException(
                status_code=403,
                detail="You can only enroll students in your own subjects",
            )

    users_collection.update_one(
        {"username": request.username}, {"$addToSet": {"subjects": request.subject}}
    )
    return {"status": "enrolled", "subject": request.subject, "user": request.username}


@router.post("/enroll-batch")
async def admin_enroll_batch(
    request: BatchEnrollmentRequest,
    user: UserInDB = Depends(require_admin_or_professor),
    users_collection=Depends(get_users_collection),
    subjects_collection=Depends(get_subjects_collection),
):
    """
    Enroll multiple students in a subject at once.
    - Professors can only enroll students in their own subjects.
    - Admins can enroll anyone in any subject.

    Returns a summary of successful and failed enrollments.
    """
    # Validate subject exists
    subject_doc = subjects_collection.find_one({"name": request.subject})
    if not subject_doc:
        raise HTTPException(
            status_code=404, detail="Subject not found. Create it first."
        )

    # Professors can only enroll in their own subjects
    if user.role == UserRole.PROFESSOR:
        if request.subject not in user.subjects:
            raise HTTPException(
                status_code=403,
                detail="You can only enroll students in your own subjects",
            )

    enrolled = []
    not_found = []
    not_students = []

    for username in request.usernames:
        target_user = users_collection.find_one({"username": username.strip()})
        if not target_user:
            not_found.append(username)
            continue

        # Only students can be enrolled
        if target_user.get("role", UserRole.STUDENT) != UserRole.STUDENT:
            not_students.append(username)
            continue

        users_collection.update_one(
            {"username": username.strip()}, {"$addToSet": {"subjects": request.subject}}
        )
        enrolled.append(username)

    return {
        "status": "completed",
        "subject": request.subject,
        "enrolled": enrolled,
        "enrolled_count": len(enrolled),
        "not_found": not_found,
        "not_students": not_students,
    }


@router.post("/unenroll")
async def admin_unenroll(
    request: AdminEnrollmentRequest,
    user: UserInDB = Depends(require_admin_or_professor),
    users_collection=Depends(get_users_collection),
):
    """
    Remove a student from a subject.
    - Professors can only unenroll from their own subjects.
    - Admins can unenroll anyone from any subject.
    """
    # Find target user
    target_user = users_collection.find_one({"username": request.username})
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Professors can only unenroll from their own subjects
    if user.role == UserRole.PROFESSOR:
        if request.subject not in user.subjects:
            raise HTTPException(
                status_code=403,
                detail="You can only unenroll students from your own subjects",
            )

    users_collection.update_one(
        {"username": request.username}, {"$pull": {"subjects": request.subject}}
    )
    return {
        "status": "unenrolled",
        "subject": request.subject,
        "user": request.username,
    }


@router.post("/assign-subject")
async def assign_subject_to_professor(
    request: AssignSubjectRequest,
    user: UserInDB = Depends(require_admin_or_professor),
    users_collection=Depends(get_users_collection),
    subjects_collection=Depends(get_subjects_collection),
):
    """
    Assign a subject to a professor. Admin only.
    """
    require_admin(user)

    # Validate subject exists
    subject_doc = subjects_collection.find_one({"name": request.subject})
    if not subject_doc:
        raise HTTPException(
            status_code=404, detail="Subject not found. Create it first."
        )

    # Find target user
    target_user = users_collection.find_one({"username": request.username})
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Target must be a professor
    if target_user.get("role") != UserRole.PROFESSOR:
        raise HTTPException(
            status_code=400, detail="Can only assign subjects to professors"
        )

    users_collection.update_one(
        {"username": request.username}, {"$addToSet": {"subjects": request.subject}}
    )
    return {
        "status": "assigned",
        "subject": request.subject,
        "professor": request.username,
    }


@router.post("/remove-subject")
async def remove_subject_from_professor(
    request: AssignSubjectRequest,
    user: UserInDB = Depends(require_admin_or_professor),
    users_collection=Depends(get_users_collection),
):
    """
    Remove a subject from a professor. Admin only.
    """
    require_admin(user)

    # Find target user
    target_user = users_collection.find_one({"username": request.username})
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    users_collection.update_one(
        {"username": request.username}, {"$pull": {"subjects": request.subject}}
    )
    return {
        "status": "removed",
        "subject": request.subject,
        "professor": request.username,
    }


@router.post("/promote")
async def promote_user(
    request: PromoteUserRequest,
    user: UserInDB = Depends(require_admin_or_professor),
    users_collection=Depends(get_users_collection),
):
    """
    Change a user's role. Admin only.
    """
    require_admin(user)

    # Find target user
    target_user = users_collection.find_one({"username": request.username})
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Can't demote yourself
    if target_user["username"] == user.username:
        raise HTTPException(status_code=400, detail="Cannot change your own role")

    users_collection.update_one(
        {"username": request.username}, {"$set": {"role": request.new_role}}
    )
    return {
        "status": "promoted",
        "user": request.username,
        "new_role": request.new_role,
    }
