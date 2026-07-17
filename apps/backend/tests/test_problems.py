import uuid
from dataclasses import dataclass

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.dependencies.auth import require_roles
from app.models import RoleName
from app.schemas.problem import ProblemCreateRequest, ProblemTestCreateRequest


def _valid_problem_payload(**overrides) -> dict:
    payload = {
        "hackathon_id": str(uuid.uuid4()),
        "title": "Semantic Resume Intelligence",
        "description": "Build a resume ranking model.",
        "max_score": 100,
        "order_index": 0,
    }
    payload.update(overrides)
    return payload


def test_valid_problem_payload_is_accepted() -> None:
    request = ProblemCreateRequest(**_valid_problem_payload())
    assert request.title == "Semantic Resume Intelligence"
    assert request.max_score == 100


@pytest.mark.parametrize("max_score", [0, -5])
def test_non_positive_max_score_is_rejected(max_score: int) -> None:
    with pytest.raises(ValidationError):
        ProblemCreateRequest(**_valid_problem_payload(max_score=max_score))


def test_empty_title_is_rejected() -> None:
    with pytest.raises(ValidationError):
        ProblemCreateRequest(**_valid_problem_payload(title=""))


def test_valid_problem_test_payload_is_accepted() -> None:
    test = ProblemTestCreateRequest(
        input_data="input", expected_output="output", is_hidden=True, weight=2.0
    )
    assert test.is_hidden is True
    assert test.weight == 2.0


def test_zero_weight_is_rejected() -> None:
    with pytest.raises(ValidationError):
        ProblemTestCreateRequest(input_data="input", expected_output="output", weight=0)


# --- RBAC: problem creation/mutation is ADMIN-only ---


@dataclass
class _FakeRole:
    name: str


@dataclass
class _FakeUser:
    role: _FakeRole


def test_student_cannot_pass_admin_only_dependency() -> None:
    dependency = require_roles(RoleName.ADMIN.value)
    student_user = _FakeUser(role=_FakeRole(name=RoleName.STUDENT.value))

    with pytest.raises(HTTPException) as exc_info:
        dependency(current_user=student_user)

    assert exc_info.value.status_code == 403


def test_admin_passes_admin_only_dependency() -> None:
    dependency = require_roles(RoleName.ADMIN.value)
    admin_user = _FakeUser(role=_FakeRole(name=RoleName.ADMIN.value))

    assert dependency(current_user=admin_user) is admin_user
