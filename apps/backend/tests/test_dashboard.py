from dataclasses import dataclass

import pytest
from fastapi import HTTPException

from app.dependencies.auth import require_roles
from app.models import RoleName


@dataclass
class _FakeRole:
    name: str


@dataclass
class _FakeUser:
    role: _FakeRole


# --- RBAC: admin-only dashboard/analytics/activity/report routes ---


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


def test_admin_cannot_pass_student_only_dependency() -> None:
    dependency = require_roles(RoleName.STUDENT.value)
    admin_user = _FakeUser(role=_FakeRole(name=RoleName.ADMIN.value))

    with pytest.raises(HTTPException) as exc_info:
        dependency(current_user=admin_user)

    assert exc_info.value.status_code == 403


# --- Score distribution bucketing (pure arithmetic, mirrors the
# repository's bucketing formula so it can be verified without a DB) ---


def _bucket_label(value: float, bucket_size: int = 10) -> str:
    bucket_start = int(value // bucket_size) * bucket_size
    return f"{bucket_start}-{bucket_start + bucket_size - 1}"


def test_score_distribution_bucketing_logic() -> None:
    assert _bucket_label(0) == "0-9"
    assert _bucket_label(9.9) == "0-9"
    assert _bucket_label(10) == "10-19"
    assert _bucket_label(95) == "90-99"
    assert _bucket_label(100) == "100-109"
