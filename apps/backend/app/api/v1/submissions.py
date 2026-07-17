import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models import User
from app.schemas.response import ApiResponse
from app.schemas.submission import (
    ExecutionResultResponse,
    SubmissionListResponse,
    SubmissionResponse,
)
from app.services.submission_service import (
    SubmissionAccessDeniedError,
    SubmissionNotFoundError,
    SubmissionService,
)

router = APIRouter(prefix="/submissions", tags=["submissions"])


def _to_response(submission) -> SubmissionResponse:
    return SubmissionResponse(
        id=submission.id,
        user_id=submission.user_id,
        problem_id=submission.problem_id,
        language=submission.language,
        status=submission.status.value,
        submitted_at=submission.submitted_at,
    )


@router.get("", response_model=ApiResponse[SubmissionListResponse])
def list_my_submissions(
    problem_id: uuid.UUID | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items, total = SubmissionService(db).list_my_submissions(current_user, problem_id)
    data = SubmissionListResponse(items=[_to_response(s) for s in items], total=total)
    return ApiResponse(success=True, message="ok", data=data)


@router.get("/{submission_id}", response_model=ApiResponse[SubmissionResponse])
def get_submission(
    submission_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        submission = SubmissionService(db).get_submission(current_user, submission_id)
    except SubmissionNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
    except SubmissionAccessDeniedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your submission")
    return ApiResponse(success=True, message="ok", data=_to_response(submission))


@router.get(
    "/{submission_id}/results", response_model=ApiResponse[list[ExecutionResultResponse]]
)
def get_submission_results(
    submission_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        rows = SubmissionService(db).get_results(current_user, submission_id)
    except SubmissionNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
    except SubmissionAccessDeniedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your submission")
    return ApiResponse(
        success=True, message="ok", data=[ExecutionResultResponse(**row) for row in rows]
    )
