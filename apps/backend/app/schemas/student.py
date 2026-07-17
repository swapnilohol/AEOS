import re
import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

PHONE_PATTERN = re.compile(r"^\+?[1-9]\d{7,14}$")


def _validate_password_complexity(password: str) -> str:
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain an uppercase letter")
    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain a lowercase letter")
    if not re.search(r"\d", password):
        raise ValueError("Password must contain a number")
    if not re.search(r"[^A-Za-z0-9]", password):
        raise ValueError("Password must contain a special character")
    return password


class StudentCreateRequest(BaseModel):
    """DTO for POST /students (admin creates a full student account + profile)."""

    full_name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password: str
    student_id: str = Field(min_length=1, max_length=50)
    college_name: str | None = None
    department: str | None = None
    semester: int | None = Field(default=None, ge=1, le=8)
    graduation_year: int | None = None
    phone_number: str | None = None
    skills: str | None = None
    resume_url: str | None = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return _validate_password_complexity(value)

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        if value is not None and not PHONE_PATTERN.match(value):
            raise ValueError("Invalid mobile phone number")
        return value


class StudentUpdateRequest(BaseModel):
    """DTO for PUT /students/{id} (admin update - full field access)."""

    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    student_id: str | None = Field(default=None, min_length=1, max_length=50)
    college_name: str | None = None
    department: str | None = None
    semester: int | None = Field(default=None, ge=1, le=8)
    graduation_year: int | None = None
    phone_number: str | None = None
    skills: str | None = None
    resume_url: str | None = None
    is_active: bool | None = None

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        if value is not None and not PHONE_PATTERN.match(value):
            raise ValueError("Invalid mobile phone number")
        return value


class StudentSelfUpdateRequest(BaseModel):
    """DTO for PUT /students/me (student self-service - restricted fields)."""

    college_name: str | None = None
    department: str | None = None
    semester: int | None = Field(default=None, ge=1, le=8)
    graduation_year: int | None = None
    phone_number: str | None = None
    skills: str | None = None
    resume_url: str | None = None

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        if value is not None and not PHONE_PATTERN.match(value):
            raise ValueError("Invalid mobile phone number")
        return value


class StudentResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    full_name: str
    email: str
    is_active: bool
    student_id: str
    college_name: str | None = None
    department: str | None = None
    semester: int | None = None
    graduation_year: int | None = None
    phone_number: str | None = None
    skills: str | None = None
    resume_url: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class StudentListResponse(BaseModel):
    items: list[StudentResponse]
    total: int
    page: int
    page_size: int


class StudentDashboardResponse(BaseModel):
    profile: StudentResponse
    total_problems: int
    submissions_count: int
    best_score: float | None = None
