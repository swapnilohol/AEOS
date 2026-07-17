import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.internal import verify_internal_token
from app.models import User
from app.schemas.response import ApiResponse
from app.schemas.scoring import (
    LeaderboardResponse,
    ScoreBreakdownResponse,
    ScoreHistoryResponse,
    ScoringCalculatedResponse,
)
from app.services.scoring_service import (
    AccessDeniedError,
    ScoreNotFoundError,
    ScoringService,
    SubmissionNotFoundError,
)

router = APIRouter(prefix="/scoring", tags=["scoring"])
internal_router = APIRouter(prefix="/internal/scoring", tags=["scoring-internal"])


# --- Internal: called by the Executor service right after execution
# completes. Authenticated with a shared static token, not a user JWT,
# since the caller isn't a logged-in user. ---


@internal_router.post(
    "/submissions/{submission_id}/calculate",
    response_model=ApiResponse[ScoringCalculatedResponse],
    dependencies=[Depends(verify_internal_token)],
)
def calculate_score(submission_id: uuid.UUID, db: Session = Depends(get_db)):
    try:
        breakdown = ScoringService(db).calculate_for_submission(submission_id)
    except SubmissionNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
    except ScoreNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No execution score exists yet for this submission",
        )
    data = ScoringCalculatedResponse(
        submission_id=breakdown.submission_id, final_score=breakdown.final_score
    )
    return ApiResponse(success=True, message="Score calculated", data=data)


# --- User-facing read APIs ---


@router.get(
    "/submissions/{submission_id}/breakdown", response_model=ApiResponse[ScoreBreakdownResponse]
)
def get_breakdown(
    submission_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        breakdown = ScoringService(db).get_breakdown(current_user, submission_id)
    except SubmissionNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
    except ScoreNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Score not yet available"
        )
    except AccessDeniedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your submission")
    return ApiResponse(success=True, message="ok", data=breakdown)


@router.get("/history", response_model=ApiResponse[ScoreHistoryResponse])
def get_history(
    problem_id: uuid.UUID | None = Query(default=None),
    user_id: uuid.UUID | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    target_user_id = user_id or current_user.id
    try:
        entries = ScoringService(db).get_history(current_user, target_user_id, problem_id)
    except AccessDeniedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Cannot view another student's history"
        )
    return ApiResponse(success=True, message="ok", data=ScoreHistoryResponse(items=entries))


@router.get("/leaderboard/{hackathon_id}", response_model=ApiResponse[LeaderboardResponse])
def get_leaderboard(
    hackathon_id: uuid.UUID,
    _current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    entries = ScoringService(db).get_leaderboard(hackathon_id)
    data = LeaderboardResponse(hackathon_id=hackathon_id, entries=entries)
    return ApiResponse(success=True, message="ok", data=data)
