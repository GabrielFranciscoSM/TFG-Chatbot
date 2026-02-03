from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    STUDENT = "student"
    PROFESSOR = "professor"
    ADMIN = "admin"


class UserPreferences(BaseModel):
    """User preferences for chatbot behavior."""

    default_test_questions: int = Field(default=5, ge=1, le=20)
    default_test_difficulty: Literal["easy", "medium", "hard"] = "medium"


class UserBase(BaseModel):
    email: EmailStr
    username: str
    role: UserRole = UserRole.STUDENT
    subjects: list[str] = []
    preferences: UserPreferences = Field(default_factory=UserPreferences)


class UserCreate(BaseModel):
    """User creation model - separate from UserBase to allow optional preferences."""

    email: EmailStr
    username: str
    password: str
    role: UserRole = UserRole.STUDENT
    subjects: list[str] = []
    preferences: UserPreferences | None = None  # Optional on creation


class UserInDB(UserBase):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class EnrollmentRequest(BaseModel):
    subject: str


class AdminEnrollmentRequest(BaseModel):
    username: str
    subject: str


class ChatSessionBase(BaseModel):
    title: str
    subject: str


class ChatSessionCreate(ChatSessionBase):
    pass


class ChatSession(ChatSessionBase):
    id: str = Field(validation_alias="_id")
    user_id: str
    created_at: datetime
    last_active: datetime
