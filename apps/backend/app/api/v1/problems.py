import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user, require_roles
from app.models import RoleName, User
from app.schemas.problem import (
    ProblemCreateRequest,
    ProblemListResponse,
    ProblemResponse,
    ProblemTestCreateRequest,
    ProblemTestResponse,
    ProblemTestUpdateRequest,
    ProblemUpdateRequest,
)
from app.schemas.response import ApiResponse
from app.services.problem_service import (
    ProblemNotFoundError,
    ProblemService,
    ProblemTestNotFoundError,
)

router = APIRouter(prefix="/problems", tags=["problems"])


@router.post("", response_model=ApiResponse[ProblemResponse])
def create_problem(
    payload: ProblemCreateRequest,
    _admin: User = Depends(require_roles(RoleName.ADMIN.value)),
    db: Session = Depends(get_db),
):
    problem = ProblemService(db).create_problem(payload)
    return ApiResponse(success=True, message="Problem created", data=ProblemResponse.model_validate(problem))


@router.get("", response_model=ApiResponse[ProblemListResponse])
def list_problems(
    hackathon_id: uuid.UUID | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items, total = ProblemService(db).list_problems(
        hackathon_id=hackathon_id, page=page, page_size=page_size
    )
    data = ProblemListResponse(
        items=[ProblemResponse.model_validate(p) for p in items],
        total=total,
        page=page,
        page_size=page_size,
    )
    return ApiResponse(success=True, message="ok", data=data)


@router.get("/{problem_id}", response_model=ApiResponse[ProblemResponse])
def get_problem(
    problem_id: uuid.UUID,
    _current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        problem = ProblemService(db).get_problem(problem_id)
    except ProblemNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")
    return ApiResponse(success=True, message="ok", data=ProblemResponse.model_validate(problem))


@router.put("/{problem_id}", response_model=ApiResponse[ProblemResponse])
def update_problem(
    problem_id: uuid.UUID,
    payload: ProblemUpdateRequest,
    _admin: User = Depends(require_roles(RoleName.ADMIN.value)),
    db: Session = Depends(get_db),
):
    try:
        problem = ProblemService(db).update_problem(problem_id, payload)
    except ProblemNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")
    return ApiResponse(success=True, message="Problem updated", data=ProblemResponse.model_validate(problem))


@router.delete("/{problem_id}", response_model=ApiResponse[None])
def delete_problem(
    problem_id: uuid.UUID,
    _admin: User = Depends(require_roles(RoleName.ADMIN.value)),
    db: Session = Depends(get_db),
):
    try:
        ProblemService(db).delete_problem(problem_id)
    except ProblemNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")
    return ApiResponse(success=True, message="Problem deleted", data=None)


# --- Problem tests (ADMIN only end-to-end: hidden expected_output values
# must never be exposed to students before the Execution Engine module) ---


@router.post("/{problem_id}/tests", response_model=ApiResponse[ProblemTestResponse])
def add_test(
    problem_id: uuid.UUID,
    payload: ProblemTestCreateRequest,
    _admin: User = Depends(require_roles(RoleName.ADMIN.value)),
    db: Session = Depends(get_db),
):
    try:
        test = ProblemService(db).add_test(problem_id, payload)
    except ProblemNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")
    return ApiResponse(success=True, message="Test case added", data=ProblemTestResponse.model_validate(test))


@router.get("/{problem_id}/tests", response_model=ApiResponse[list[ProblemTestResponse]])
def list_tests(
    problem_id: uuid.UUID,
    _admin: User = Depends(require_roles(RoleName.ADMIN.value)),
    db: Session = Depends(get_db),
):
    try:
        tests = ProblemService(db).list_tests(problem_id)
    except ProblemNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")
    return ApiResponse(
        success=True, message="ok", data=[ProblemTestResponse.model_validate(t) for t in tests]
    )


@router.put("/{problem_id}/tests/{test_id}", response_model=ApiResponse[ProblemTestResponse])
def update_test(
    problem_id: uuid.UUID,
    test_id: uuid.UUID,
    payload: ProblemTestUpdateRequest,
    _admin: User = Depends(require_roles(RoleName.ADMIN.value)),
    db: Session = Depends(get_db),
):
    try:
        test = ProblemService(db).update_test(problem_id, test_id, payload)
    except ProblemTestNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test case not found")
    return ApiResponse(success=True, message="Test case updated", data=ProblemTestResponse.model_validate(test))


@router.delete("/{problem_id}/tests/{test_id}", response_model=ApiResponse[None])
def delete_test(
    problem_id: uuid.UUID,
    test_id: uuid.UUID,
    _admin: User = Depends(require_roles(RoleName.ADMIN.value)),
    db: Session = Depends(get_db),
):
    try:
        ProblemService(db).delete_test(problem_id, test_id)
    except ProblemTestNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test case not found")
    return ApiResponse(success=True, message="Test case deleted", data=None)
