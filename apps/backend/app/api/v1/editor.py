import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import require_roles
from app.models import EditorSession, RoleName, User
from app.schemas.editor import (
    DraftResponse,
    EditorSessionResponse,
    SaveDraftRequest,
    StartSessionRequest,
    SubmissionPreparedResponse,
    SubmitSolutionRequest,
    WorkspaceResponse,
)
from app.schemas.response import ApiResponse
from app.services.editor_service import (
    DraftNotFoundError,
    EditorService,
    NoDraftToSubmitError,
    ProblemNotFoundError,
    SessionNotFoundError,
    SessionNotOwnedError,
)
from app.services.problem_service import ProblemNotFoundError as ProblemServiceNotFoundError

router = APIRouter(prefix="/editor", tags=["editor"])


def _session_response(session: EditorSession) -> EditorSessionResponse:
    return EditorSessionResponse(
        id=session.id,
        user_id=session.user_id,
        problem_id=session.problem_id,
        language=session.language,
        status=session.status.value,
        started_at=session.started_at,
        last_active_at=session.last_active_at,
        ended_at=session.ended_at,
    )


# --- Drafts (STUDENT, own problem draft only) ---


@router.put("/problems/{problem_id}/draft", response_model=ApiResponse[DraftResponse])
def save_draft(
    problem_id: uuid.UUID,
    payload: SaveDraftRequest,
    current_user: User = Depends(require_roles(RoleName.STUDENT.value)),
    db: Session = Depends(get_db),
):
    try:
        draft = EditorService(db).save_draft(current_user, problem_id, payload)
    except (ProblemNotFoundError, ProblemServiceNotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")
    return ApiResponse(
        success=True, message="Draft saved", data=DraftResponse.model_validate(draft)
    )


@router.get("/problems/{problem_id}/draft", response_model=ApiResponse[DraftResponse])
def get_draft(
    problem_id: uuid.UUID,
    current_user: User = Depends(require_roles(RoleName.STUDENT.value)),
    db: Session = Depends(get_db),
):
    try:
        draft = EditorService(db).get_draft(current_user, problem_id)
    except (ProblemNotFoundError, ProblemServiceNotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")
    except DraftNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No draft saved yet")
    return ApiResponse(success=True, message="ok", data=DraftResponse.model_validate(draft))


# --- Sessions (STUDENT for lifecycle, ADMIN for monitoring) ---


@router.post("/problems/{problem_id}/sessions", response_model=ApiResponse[EditorSessionResponse])
def start_session(
    problem_id: uuid.UUID,
    payload: StartSessionRequest,
    current_user: User = Depends(require_roles(RoleName.STUDENT.value)),
    db: Session = Depends(get_db),
):
    try:
        session = EditorService(db).start_session(current_user, problem_id, payload.language)
    except (ProblemNotFoundError, ProblemServiceNotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")
    return ApiResponse(success=True, message="Session started", data=_session_response(session))


@router.patch(
    "/sessions/{session_id}/heartbeat", response_model=ApiResponse[EditorSessionResponse]
)
def heartbeat_session(
    session_id: uuid.UUID,
    current_user: User = Depends(require_roles(RoleName.STUDENT.value)),
    db: Session = Depends(get_db),
):
    try:
        session = EditorService(db).heartbeat_session(current_user, session_id)
    except SessionNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    except SessionNotOwnedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your session")
    return ApiResponse(success=True, message="ok", data=_session_response(session))


@router.post("/sessions/{session_id}/end", response_model=ApiResponse[EditorSessionResponse])
def end_session(
    session_id: uuid.UUID,
    current_user: User = Depends(require_roles(RoleName.STUDENT.value)),
    db: Session = Depends(get_db),
):
    try:
        session = EditorService(db).end_session(current_user, session_id)
    except SessionNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    except SessionNotOwnedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your session")
    return ApiResponse(success=True, message="Session ended", data=_session_response(session))


@router.get("/sessions/active", response_model=ApiResponse[list[EditorSessionResponse]])
def list_active_sessions(
    _admin: User = Depends(require_roles(RoleName.ADMIN.value)),
    db: Session = Depends(get_db),
):
    sessions = EditorService(db).list_active_sessions_for_admin()
    return ApiResponse(
        success=True, message="ok", data=[_session_response(s) for s in sessions]
    )


# --- Submission preparation (STUDENT) ---
# NOTE: this creates a PENDING Submission row only. Running code against
# test cases is out of scope here — that is the Execution Engine module.


@router.post(
    "/problems/{problem_id}/submit", response_model=ApiResponse[SubmissionPreparedResponse]
)
def submit_solution(
    problem_id: uuid.UUID,
    payload: SubmitSolutionRequest,
    current_user: User = Depends(require_roles(RoleName.STUDENT.value)),
    db: Session = Depends(get_db),
):
    try:
        submission = EditorService(db).submit_solution(current_user, problem_id, payload)
    except (ProblemNotFoundError, ProblemServiceNotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")
    except NoDraftToSubmitError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No code provided and no saved draft to submit",
        )
    data = SubmissionPreparedResponse(
        submission_id=submission.id,
        problem_id=submission.problem_id,
        status=submission.status.value,
        submitted_at=submission.submitted_at,
    )
    return ApiResponse(success=True, message="Submission received", data=data)


# --- Workspace aggregation (STUDENT, feeds the Editor Dashboard) ---


@router.get("/problems/{problem_id}/workspace", response_model=ApiResponse[WorkspaceResponse])
def get_workspace(
    problem_id: uuid.UUID,
    current_user: User = Depends(require_roles(RoleName.STUDENT.value)),
    db: Session = Depends(get_db),
):
    try:
        workspace = EditorService(db).get_workspace(current_user, problem_id)
    except (ProblemNotFoundError, ProblemServiceNotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")

    data = WorkspaceResponse(
        problem=workspace["problem"],
        student_full_name=workspace["student_full_name"],
        remaining_seconds=workspace["remaining_seconds"],
        draft=DraftResponse.model_validate(workspace["draft"]) if workspace["draft"] else None,
        active_session=(
            _session_response(workspace["active_session"])
            if workspace["active_session"]
            else None
        ),
        latest_submission_status=workspace["latest_submission_status"],
    )
    return ApiResponse(success=True, message="ok", data=data)
