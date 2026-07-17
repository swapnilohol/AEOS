import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ActiveHackathonSummary(BaseModel):
    id: uuid.UUID
    title: str
    start_time: datetime | None = None
    end_time: datetime | None = None


class LiveStatus(BaseModel):
    active_students: int
    running_executions: int
    completed_submissions: int
    failed_executions: int


class AdminOverviewResponse(BaseModel):
    total_students: int
    active_students: int
    total_problems: int
    total_submissions: int
    completed_assessments: int
    average_score: float | None = None
    active_hackathon: ActiveHackathonSummary | None = None
    live_status: LiveStatus


class ProblemCompletionRow(BaseModel):
    problem_id: uuid.UUID
    title: str
    difficulty_multiplier: float
    attempted_count: int
    solved_count: int
    completion_rate_percent: float


class ExecutionStats(BaseModel):
    timeout_count: int
    failed_executions: int
    average_execution_time_ms: float | None = None


class AdminAnalyticsResponse(BaseModel):
    average_score: float | None = None
    problem_completion: list[ProblemCompletionRow]
    score_distribution: dict[str, int]
    execution_stats: ExecutionStats


class ActivityLogEntry(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    activity_type: str
    metadata: dict[str, Any] | None = None
    created_at: datetime


class ActivityFeedResponse(BaseModel):
    items: list[ActivityLogEntry]


class StudentProfileSummary(BaseModel):
    full_name: str
    college_name: str | None = None
    department: str | None = None
    semester: int | None = None


class StudentProgress(BaseModel):
    problems_attempted: int
    problems_solved: int
    total_problems: int
    completion_percent: float


class StudentRankInfo(BaseModel):
    rank: int | None = None
    total_score: float | None = None
    total_participants: int | None = None


class StudentOverviewResponse(BaseModel):
    profile: StudentProfileSummary
    hackathon_status: str
    remaining_seconds: int | None = None
    progress: StudentProgress
    rank: StudentRankInfo | None = None


class ScoreHistoryPoint(BaseModel):
    submission_id: uuid.UUID
    problem_id: uuid.UUID
    final_score: float | None = None
    max_points: float
    achieved_at: datetime


class StudentPerformanceResponse(BaseModel):
    score_history: list[ScoreHistoryPoint]


class StudentLeaderboardEntry(BaseModel):
    rank: int | None = None
    user_id: uuid.UUID
    full_name: str
    total_score: float


class StudentLeaderboardResponse(BaseModel):
    hackathon_id: uuid.UUID
    total_participants: int
    own_rank: int | None = None
    own_total_score: float | None = None
    top_entries: list[StudentLeaderboardEntry]
