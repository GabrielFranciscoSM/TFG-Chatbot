from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    STUDENT = "student"
    PROFESSOR = "professor"
    ADMIN = "admin"


class UserBase(BaseModel):
    email: EmailStr
    username: str
    role: UserRole = UserRole.STUDENT
    subjects: list[str] = []


class UserCreate(UserBase):
    password: str


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
