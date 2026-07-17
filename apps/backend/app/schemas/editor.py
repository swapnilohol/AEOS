import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class SaveDraftRequest(BaseModel):
    language: str = Field(default="python", min_length=1, max_length=50)
    code: str = Field(default="")


class DraftResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    problem_id: uuid.UUID
    language: str
    code: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class StartSessionRequest(BaseModel):
    language: str = Field(default="python", min_length=1, max_length=50)


class EditorSessionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    problem_id: uuid.UUID
    language: str
    status: str
    started_at: datetime
    last_active_at: datetime
    ended_at: datetime | None = None

    model_config = {"from_attributes": True}


class SubmitSolutionRequest(BaseModel):
    """If code/language are omitted, the student's saved draft is used."""

    code: str | None = None
    language: str | None = Field(default=None, max_length=50)


class SubmissionPreparedResponse(BaseModel):
    submission_id: uuid.UUID
    problem_id: uuid.UUID
    status: str
    submitted_at: datetime


class ProblemSummary(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    max_score: int


class WorkspaceResponse(BaseModel):
    problem: ProblemSummary
    student_full_name: str
    remaining_seconds: int | None = None
    draft: DraftResponse | None = None
    active_session: EditorSessionResponse | None = None
    latest_submission_status: str | None = None
