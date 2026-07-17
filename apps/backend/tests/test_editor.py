from dataclasses import dataclass

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.dependencies.auth import require_roles
from app.models import RoleName
from app.schemas.editor import SaveDraftRequest, StartSessionRequest, SubmitSolutionRequest


def test_save_draft_request_defaults() -> None:
    request = SaveDraftRequest(code="print('hi')")
    assert request.language == "python"
    assert request.code == "print('hi')"


def test_save_draft_request_empty_code_allowed() -> None:
    # Empty drafts must be saveable (a student who hasn't typed anything yet).
    request = SaveDraftRequest()
    assert request.code == ""


def test_start_session_request_requires_language_min_length() -> None:
    with pytest.raises(ValidationError):
        StartSessionRequest(language="")


def test_submit_solution_request_allows_omitted_code_and_language() -> None:
    # Submitting with no body means "use my saved draft" — must not raise.
    request = SubmitSolutionRequest()
    assert request.code is None
    assert request.language is None


def test_submit_solution_request_accepts_explicit_code() -> None:
    request = SubmitSolutionRequest(code="print(1)", language="python")
    assert request.code == "print(1)"


# --- RBAC: editor draft/session/submit routes are STUDENT-only ---


@dataclass
class _FakeRole:
    name: str


@dataclass
class _FakeUser:
    role: _FakeRole


def test_admin_cannot_pass_student_only_dependency() -> None:
    dependency = require_roles(RoleName.STUDENT.value)
    admin_user = _FakeUser(role=_FakeRole(name=RoleName.ADMIN.value))

    with pytest.raises(HTTPException) as exc_info:
        dependency(current_user=admin_user)

    assert exc_info.value.status_code == 403


def test_student_passes_student_only_dependency() -> None:
    dependency = require_roles(RoleName.STUDENT.value)
    student_user = _FakeUser(role=_FakeRole(name=RoleName.STUDENT.value))

    assert dependency(current_user=student_user) is student_user


def test_student_cannot_pass_admin_only_monitoring_dependency() -> None:
    dependency = require_roles(RoleName.ADMIN.value)
    student_user = _FakeUser(role=_FakeRole(name=RoleName.STUDENT.value))

    with pytest.raises(HTTPException) as exc_info:
        dependency(current_user=student_user)

    assert exc_info.value.status_code == 403
