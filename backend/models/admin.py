from pydantic import BaseModel

from .common import UserRole


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
