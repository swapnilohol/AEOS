from dataclasses import dataclass

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.dependencies.auth import require_roles
from app.models import RoleName
from app.schemas.student import StudentCreateRequest


def _valid_payload(**overrides) -> dict:
    payload = {
        "full_name": "Ada Lovelace",
        "email": "ada@example.com",
        "password": "Str0ng!Pass",
        "student_id": "STU-001",
        "semester": 4,
        "phone_number": "+919876543210",
    }
    payload.update(overrides)
    return payload


# --- Password complexity ---


def test_valid_password_is_accepted() -> None:
    request = StudentCreateRequest(**_valid_payload())
    assert request.password == "Str0ng!Pass"


@pytest.mark.parametrize(
    "bad_password",
    [
        "short1!",  # too short
        "alllowercase1!",  # no uppercase
        "ALLUPPERCASE1!",  # no lowercase
        "NoNumbersHere!",  # no digit
        "NoSpecialChar123",  # no special character
    ],
)
def test_weak_passwords_are_rejected(bad_password: str) -> None:
    with pytest.raises(ValidationError):
        StudentCreateRequest(**_valid_payload(password=bad_password))


# --- Semester range (1-8) ---


@pytest.mark.parametrize("semester", [1, 4, 8])
def test_valid_semester_is_accepted(semester: int) -> None:
    request = StudentCreateRequest(**_valid_payload(semester=semester))
    assert request.semester == semester


@pytest.mark.parametrize("semester", [0, 9, -1])
def test_out_of_range_semester_is_rejected(semester: int) -> None:
    with pytest.raises(ValidationError):
        StudentCreateRequest(**_valid_payload(semester=semester))


# --- Phone number format ---


def test_valid_phone_number_is_accepted() -> None:
    request = StudentCreateRequest(**_valid_payload(phone_number="+14155552671"))
    assert request.phone_number == "+14155552671"


@pytest.mark.parametrize("bad_phone", ["abc123", "12", "phone-number"])
def test_invalid_phone_number_is_rejected(bad_phone: str) -> None:
    with pytest.raises(ValidationError):
        StudentCreateRequest(**_valid_payload(phone_number=bad_phone))


# --- student_id required ---


def test_missing_student_id_is_rejected() -> None:
    payload = _valid_payload()
    del payload["student_id"]
    with pytest.raises(ValidationError):
        StudentCreateRequest(**payload)


# --- RBAC: admin-only routes must reject STUDENT and accept ADMIN ---


@dataclass
class _FakeRole:
    name: str


@dataclass
class _FakeUser:
    role: _FakeRole


def test_require_roles_rejects_student_for_admin_only_route() -> None:
    dependency = require_roles(RoleName.ADMIN.value)
    student_user = _FakeUser(role=_FakeRole(name=RoleName.STUDENT.value))

    with pytest.raises(HTTPException) as exc_info:
        dependency(current_user=student_user)

    assert exc_info.value.status_code == 403


def test_require_roles_allows_admin_for_admin_only_route() -> None:
    dependency = require_roles(RoleName.ADMIN.value)
    admin_user = _FakeUser(role=_FakeRole(name=RoleName.ADMIN.value))

    result = dependency(current_user=admin_user)

    assert result is admin_user
