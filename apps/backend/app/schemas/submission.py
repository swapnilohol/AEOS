import uuid
from datetime import datetime

from pydantic import BaseModel


class SubmissionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    problem_id: uuid.UUID
    language: str
    status: str
    submitted_at: datetime

    model_config = {"from_attributes": True}


class SubmissionListResponse(BaseModel):
    items: list[SubmissionResponse]
    total: int


class ExecutionResultResponse(BaseModel):
    id: uuid.UUID
    problem_test_id: uuid.UUID
    is_hidden: bool
    passed: bool
    execution_time_ms: int | None = None
    # Redacted (set to None) for hidden tests when the viewer is not ADMIN.
    actual_output: str | None = None
    error_message: str | None = None
