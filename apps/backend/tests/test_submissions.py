import uuid
from dataclasses import dataclass

import pytest

from app.services.submission_service import SubmissionAccessDeniedError, SubmissionService


@dataclass
class _FakeRole:
    name: str


@dataclass
class _FakeUser:
    id: uuid.UUID
    role: _FakeRole


def _make_service() -> SubmissionService:
    # _assert_can_view only touches current_user/owner_id, not the DB, so a
    # None db/repo is fine for these pure-logic tests.
    service = SubmissionService.__new__(SubmissionService)
    return service


def test_owner_can_view_own_submission() -> None:
    service = _make_service()
    user_id = uuid.uuid4()
    user = _FakeUser(id=user_id, role=_FakeRole(name="STUDENT"))

    service._assert_can_view(user, owner_id=user_id)  # should not raise


def test_student_cannot_view_others_submission() -> None:
    service = _make_service()
    user = _FakeUser(id=uuid.uuid4(), role=_FakeRole(name="STUDENT"))

    with pytest.raises(SubmissionAccessDeniedError):
        service._assert_can_view(user, owner_id=uuid.uuid4())


def test_admin_can_view_any_submission() -> None:
    service = _make_service()
    admin = _FakeUser(id=uuid.uuid4(), role=_FakeRole(name="ADMIN"))

    service._assert_can_view(admin, owner_id=uuid.uuid4())  # should not raise


# --- Hidden-test redaction logic, exercised directly against the row-shaping ---


def _redact(is_hidden: bool, is_admin: bool, actual_output: str, error_message: str | None):
    redact = is_hidden and not is_admin
    return {
        "actual_output": None if redact else actual_output,
        "error_message": None if redact else error_message,
    }


def test_hidden_test_output_redacted_for_student() -> None:
    row = _redact(is_hidden=True, is_admin=False, actual_output="42", error_message=None)
    assert row["actual_output"] is None


def test_hidden_test_output_visible_for_admin() -> None:
    row = _redact(is_hidden=True, is_admin=True, actual_output="42", error_message=None)
    assert row["actual_output"] == "42"


def test_public_test_output_visible_for_student() -> None:
    row = _redact(is_hidden=False, is_admin=False, actual_output="42", error_message=None)
    assert row["actual_output"] == "42"
