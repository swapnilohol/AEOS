import uuid
from datetime import datetime

from pydantic import BaseModel


class ActiveHackathonSummary(BaseModel):
    id: uuid.UUID
    title: str
    start_time: datetime | None = None
    end_time: datetime | None = None
    problem_count: int


class SubmissionStatusBreakdown(BaseModel):
    pending: int
    running: int
    completed: int
    failed: int


class TopScoreEntry(BaseModel):
    user_id: uuid.UUID
    full_name: str
    total_points: float


class AdminDashboardResponse(BaseModel):
    total_students: int
    total_problems: int
    total_submissions: int
    total_violations: int
    active_hackathon: ActiveHackathonSummary | None = None
    submission_status_breakdown: SubmissionStatusBreakdown
    top_scores: list[TopScoreEntry]
