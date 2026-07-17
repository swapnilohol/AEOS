import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    EditorSession,
    EditorSessionStatus,
    ExecutionResult,
    Problem,
    Role,
    RoleName,
    Score,
    ScoreBreakdown,
    Submission,
    SubmissionStatus,
    User,
)


class DashboardRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def count_active_students(self) -> int:
        """"Active" = currently has an open editor session (Editor Module).
        A simple, honest proxy for live activity at 10-student scale."""
        stmt = (
            select(func.count(func.distinct(EditorSession.user_id)))
            .select_from(EditorSession)
            .where(EditorSession.status == EditorSessionStatus.ACTIVE)
        )
        return self.db.execute(stmt).scalar_one()

    def count_completed_assessments(self) -> int:
        stmt = (
            select(func.count())
            .select_from(Submission)
            .where(Submission.status == SubmissionStatus.COMPLETED)
        )
        return self.db.execute(stmt).scalar_one()

    def average_final_score(self) -> float | None:
        stmt = select(func.avg(ScoreBreakdown.final_score))
        return self.db.execute(stmt).scalar_one_or_none()

    def running_executions_count(self) -> int:
        stmt = (
            select(func.count())
            .select_from(Submission)
            .where(Submission.status == SubmissionStatus.RUNNING)
        )
        return self.db.execute(stmt).scalar_one()

    def failed_executions_count(self) -> int:
        stmt = (
            select(func.count())
            .select_from(Submission)
            .where(Submission.status == SubmissionStatus.FAILED)
        )
        return self.db.execute(stmt).scalar_one()

    def timeout_count(self) -> int:
        stmt = (
            select(func.count())
            .select_from(ExecutionResult)
            .where(ExecutionResult.error_message.ilike("%timed out%"))
        )
        return self.db.execute(stmt).scalar_one()

    def average_execution_time_ms(self) -> float | None:
        stmt = select(func.avg(ExecutionResult.execution_time_ms)).where(
            ExecutionResult.execution_time_ms.isnot(None)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def problem_completion_rates(self, total_students: int) -> list[dict]:
        """Per problem: distinct students with at least one submission, and
        with at least one fully-passing submission, out of total_students."""
        attempted_stmt = (
            select(Submission.problem_id, func.count(func.distinct(Submission.user_id)))
            .group_by(Submission.problem_id)
        )
        attempted = dict(self.db.execute(attempted_stmt).all())

        solved_stmt = (
            select(Score.problem_id, func.count(func.distinct(Score.user_id)))
            .join(ScoreBreakdown, ScoreBreakdown.score_id == Score.id)
            .where(ScoreBreakdown.final_score >= Score.max_points)
            .group_by(Score.problem_id)
        )
        solved = dict(self.db.execute(solved_stmt).all())

        problems = list(self.db.execute(select(Problem)).scalars().all())
        rows = []
        for problem in problems:
            attempted_count = attempted.get(problem.id, 0)
            solved_count = solved.get(problem.id, 0)
            rate = (solved_count / total_students * 100) if total_students else 0.0
            rows.append(
                {
                    "problem_id": problem.id,
                    "title": problem.title,
                    "difficulty_multiplier": problem.difficulty_multiplier,
                    "attempted_count": attempted_count,
                    "solved_count": solved_count,
                    "completion_rate_percent": round(rate, 1),
                }
            )
        return rows

    def score_distribution(self, bucket_size: int = 10) -> dict[str, int]:
        """Histogram of final_score into fixed-width buckets, e.g. '0-9',
        '10-19', ... '90-100'."""
        stmt = select(ScoreBreakdown.final_score)
        values = [row[0] for row in self.db.execute(stmt).all()]

        buckets: dict[str, int] = {}
        for value in values:
            bucket_start = int(value // bucket_size) * bucket_size
            label = f"{bucket_start}-{bucket_start + bucket_size - 1}"
            buckets[label] = buckets.get(label, 0) + 1
        return buckets

    def student_submission_counts(self, user_id: uuid.UUID) -> dict[str, int]:
        attempted_stmt = (
            select(func.count(func.distinct(Submission.problem_id)))
            .select_from(Submission)
            .where(Submission.user_id == user_id)
        )
        attempted = self.db.execute(attempted_stmt).scalar_one()

        solved_stmt = (
            select(func.count(func.distinct(Score.problem_id)))
            .select_from(Score)
            .join(ScoreBreakdown, ScoreBreakdown.score_id == Score.id)
            .where(Score.user_id == user_id, ScoreBreakdown.final_score >= Score.max_points)
        )
        solved = self.db.execute(solved_stmt).scalar_one()

        return {"attempted": attempted, "solved": solved}

    def total_students(self) -> int:
        stmt = (
            select(func.count())
            .select_from(User)
            .join(Role, User.role_id == Role.id)
            .where(Role.name == RoleName.STUDENT.value)
        )
        return self.db.execute(stmt).scalar_one()
