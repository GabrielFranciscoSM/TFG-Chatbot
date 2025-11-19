from enum import Enum

from pydantic import BaseModel, EmailStr


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
