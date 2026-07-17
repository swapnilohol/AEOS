import uuid
from datetime import datetime

from pydantic import BaseModel


class ScoreBreakdownResponse(BaseModel):
    score_id: uuid.UUID
    submission_id: uuid.UUID
    problem_id: uuid.UUID
    functional_score: float
    performance_factor: float
    difficulty_multiplier: float
    penalty_factor: float
    quality_score: float | None = None
    final_score: float
    max_points: float
    computed_at: datetime


class ScoreHistoryEntry(BaseModel):
    submission_id: uuid.UUID
    problem_id: uuid.UUID
    final_score: float | None = None
    max_points: float
    submitted_at: datetime


class ScoreHistoryResponse(BaseModel):
    items: list[ScoreHistoryEntry]


class LeaderboardEntryResponse(BaseModel):
    rank: int
    user_id: uuid.UUID
    full_name: str
    total_score: float


class LeaderboardResponse(BaseModel):
    hackathon_id: uuid.UUID
    entries: list[LeaderboardEntryResponse]


class ScoringCalculatedResponse(BaseModel):
    submission_id: uuid.UUID
    final_score: float
