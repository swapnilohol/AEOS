import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user, require_roles
from app.models import RoleName, User
from app.schemas.response import ApiResponse
from app.schemas.student import (
    StudentCreateRequest,
    StudentDashboardResponse,
    StudentListResponse,
    StudentResponse,
    StudentSelfUpdateRequest,
    StudentUpdateRequest,
)
from app.services.student_service import (
    DuplicateStudentError,
    StudentNotFoundError,
    StudentService,
)

router = APIRouter(prefix="/students", tags=["students"])


def _to_response(profile, user: User) -> StudentResponse:
    return StudentResponse(
        id=profile.id,
        user_id=user.id,
        full_name=user.full_name,
        email=user.email,
        is_active=user.is_active,
        student_id=profile.student_id,
        college_name=profile.college_name,
        department=profile.department,
        semester=profile.semester,
        graduation_year=profile.graduation_year,
        phone_number=profile.phone_number,
        skills=profile.skills,
        resume_url=profile.resume_url,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


# --- Student self-service routes (declared before /{id} to avoid path collision) ---


@router.get("/me", response_model=ApiResponse[StudentResponse])
def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = StudentService(db)
    try:
        profile, user = service.get_own_profile(current_user)
    except StudentNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found"
        )
    return ApiResponse(success=True, message="ok", data=_to_response(profile, user))


@router.put("/me", response_model=ApiResponse[StudentResponse])
def update_my_profile(
    payload: StudentSelfUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = StudentService(db)
    try:
        profile, user = service.update_own_profile(current_user, payload)
    except StudentNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found"
        )
    return ApiResponse(success=True, message="Profile updated", data=_to_response(profile, user))


@router.get("/dashboard", response_model=ApiResponse[StudentDashboardResponse])
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = StudentService(db)
    try:
        profile, user, total_problems, submissions_count, best_score = service.get_dashboard(
            current_user
        )
    except StudentNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found"
        )
    data = StudentDashboardResponse(
        profile=_to_response(profile, user),
        total_problems=total_problems,
        submissions_count=submissions_count,
        best_score=best_score,
    )
    return ApiResponse(success=True, message="ok", data=data)


# --- Admin routes ---


@router.post("", response_model=ApiResponse[StudentResponse])
def create_student(
    payload: StudentCreateRequest,
    _admin: User = Depends(require_roles(RoleName.ADMIN.value)),
    db: Session = Depends(get_db),
):
    service = StudentService(db)
    try:
        profile, user = service.create_student(payload)
    except DuplicateStudentError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    return ApiResponse(
        success=True, message="Student created", data=_to_response(profile, user)
    )


@router.get("", response_model=ApiResponse[StudentListResponse])
def list_students(
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _admin: User = Depends(require_roles(RoleName.ADMIN.value)),
    db: Session = Depends(get_db),
):
    service = StudentService(db)
    items, total = service.list_students(search=search, page=page, page_size=page_size)
    data = StudentListResponse(
        items=[_to_response(profile, profile.user) for profile in items],
        total=total,
        page=page,
        page_size=page_size,
    )
    return ApiResponse(success=True, message="ok", data=data)


@router.get("/{student_profile_id}", response_model=ApiResponse[StudentResponse])
def get_student(
    student_profile_id: uuid.UUID,
    _admin: User = Depends(require_roles(RoleName.ADMIN.value)),
    db: Session = Depends(get_db),
):
    service = StudentService(db)
    try:
        profile, user = service.get_student(student_profile_id)
    except StudentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return ApiResponse(success=True, message="ok", data=_to_response(profile, user))


@router.put("/{student_profile_id}", response_model=ApiResponse[StudentResponse])
def update_student(
    student_profile_id: uuid.UUID,
    payload: StudentUpdateRequest,
    _admin: User = Depends(require_roles(RoleName.ADMIN.value)),
    db: Session = Depends(get_db),
):
    service = StudentService(db)
    try:
        profile, user = service.update_student(student_profile_id, payload)
    except StudentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    except DuplicateStudentError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    return ApiResponse(success=True, message="Student updated", data=_to_response(profile, user))


@router.delete("/{student_profile_id}", response_model=ApiResponse[None])
def delete_student(
    student_profile_id: uuid.UUID,
    _admin: User = Depends(require_roles(RoleName.ADMIN.value)),
    db: Session = Depends(get_db),
):
    service = StudentService(db)
    try:
        service.delete_student(student_profile_id)
    except StudentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return ApiResponse(success=True, message="Student deleted", data=None)
