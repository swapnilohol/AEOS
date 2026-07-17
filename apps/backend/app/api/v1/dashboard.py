import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user, require_roles
from app.models import RoleName, User
from app.schemas.response import ApiResponse
from app.schemas.dashboard import (
    ActivityFeedResponse,
    AdminAnalyticsResponse,
    AdminOverviewResponse,
    StudentLeaderboardResponse,
    StudentOverviewResponse,
    StudentPerformanceResponse,
)
from app.services.dashboard_service import (
    DashboardDataUnavailableError,
    DashboardService,
    StudentProfileRequiredError,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


# --- Admin dashboard ---


@router.get("/admin/overview", response_model=ApiResponse[AdminOverviewResponse])
def admin_overview(
    _admin: User = Depends(require_roles(RoleName.ADMIN.value)),
    db: Session = Depends(get_db),
):
    data = DashboardService(db).get_admin_overview()
    return ApiResponse(success=True, message="ok", data=data)


@router.get("/admin/analytics", response_model=ApiResponse[AdminAnalyticsResponse])
def admin_analytics(
    _admin: User = Depends(require_roles(RoleName.ADMIN.value)),
    db: Session = Depends(get_db),
):
    data = DashboardService(db).get_admin_analytics()
    return ApiResponse(success=True, message="ok", data=data)


@router.get("/admin/activity", response_model=ApiResponse[ActivityFeedResponse])
def admin_activity(
    limit: int = Query(default=20, ge=1, le=100),
    _admin: User = Depends(require_roles(RoleName.ADMIN.value)),
    db: Session = Depends(get_db),
):
    items = DashboardService(db).get_admin_activity(limit)
    return ApiResponse(success=True, message="ok", data=ActivityFeedResponse(items=items))


# --- Admin reports (structured JSON, no file/PDF generation) ---


@router.get("/admin/reports/student/{user_id}", response_model=ApiResponse[dict[str, Any]])
def student_report(
    user_id: uuid.UUID,
    _admin: User = Depends(require_roles(RoleName.ADMIN.value)),
    db: Session = Depends(get_db),
):
    try:
        data = DashboardService(db).get_student_report(user_id)
    except DashboardDataUnavailableError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No student profile found"
        )
    return ApiResponse(success=True, message="ok", data=data)


@router.get("/admin/reports/submissions", response_model=ApiResponse[dict[str, Any]])
def submission_report(
    _admin: User = Depends(require_roles(RoleName.ADMIN.value)),
    db: Session = Depends(get_db),
):
    data = DashboardService(db).get_submission_report()
    return ApiResponse(success=True, message="ok", data=data)


@router.get("/admin/reports/hackathon-summary", response_model=ApiResponse[dict[str, Any]])
def hackathon_summary(
    hackathon_id: uuid.UUID | None = Query(default=None),
    _admin: User = Depends(require_roles(RoleName.ADMIN.value)),
    db: Session = Depends(get_db),
):
    data = DashboardService(db).get_hackathon_summary(hackathon_id)
    return ApiResponse(success=True, message="ok", data=data)


# --- Student dashboard ---


@router.get("/student/overview", response_model=ApiResponse[StudentOverviewResponse])
def student_overview(
    current_user: User = Depends(require_roles(RoleName.STUDENT.value)),
    db: Session = Depends(get_db),
):
    try:
        data = DashboardService(db).get_student_overview(current_user)
    except StudentProfileRequiredError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No student profile found"
        )
    return ApiResponse(success=True, message="ok", data=data)


@router.get("/student/performance", response_model=ApiResponse[StudentPerformanceResponse])
def student_performance(
    current_user: User = Depends(require_roles(RoleName.STUDENT.value)),
    db: Session = Depends(get_db),
):
    data = DashboardService(db).get_student_performance(current_user)
    return ApiResponse(success=True, message="ok", data=data)


@router.get("/student/leaderboard", response_model=ApiResponse[StudentLeaderboardResponse])
def student_leaderboard(
    hackathon_id: uuid.UUID | None = Query(default=None),
    current_user: User = Depends(require_roles(RoleName.STUDENT.value)),
    db: Session = Depends(get_db),
):
    try:
        data = DashboardService(db).get_student_leaderboard(current_user, hackathon_id)
    except DashboardDataUnavailableError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No active hackathon"
        )
    return ApiResponse(success=True, message="ok", data=data)
