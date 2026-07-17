import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    ExecutionResult,
    Hackathon,
    LeaderboardEntry,
    Problem,
    Score,
    ScoreBreakdown,
    Submission,
    User,
)


class ScoringRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    # --- Reads needed to calculate a single submission's breakdown ---

    def get_submission(self, submission_id: uuid.UUID) -> Submission | None:
        return self.db.get(Submission, submission_id)

    def get_problem(self, problem_id: uuid.UUID) -> Problem | None:
        return self.db.get(Problem, problem_id)

    def get_score_for_submission(self, submission_id: uuid.UUID) -> Score | None:
        stmt = select(Score).where(Score.submission_id == submission_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_hackathon(self, hackathon_id: uuid.UUID) -> Hackathon | None:
        return self.db.get(Hackathon, hackathon_id)

    def avg_execution_time_for_passed_tests(self, submission_id: uuid.UUID) -> float | None:
        stmt = select(func.avg(ExecutionResult.execution_time_ms)).where(
            ExecutionResult.submission_id == submission_id,
            ExecutionResult.passed.is_(True),
            ExecutionResult.execution_time_ms.isnot(None),
        )
        return self.db.execute(stmt).scalar_one_or_none()

    # --- Breakdown persistence (1:1 with Score) ---

    def get_breakdown_for_score(self, score_id: uuid.UUID) -> ScoreBreakdown | None:
        stmt = select(ScoreBreakdown).where(ScoreBreakdown.score_id == score_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def upsert_breakdown(self, score_id: uuid.UUID, **fields) -> ScoreBreakdown:
        breakdown = self.get_breakdown_for_score(score_id)
        if breakdown is None:
            breakdown = ScoreBreakdown(score_id=score_id, **fields)
            self.db.add(breakdown)
        else:
            for key, value in fields.items():
                setattr(breakdown, key, value)
        self.db.flush()
        return breakdown

    # --- Score history for a user+problem (uses existing Score rows) ---

    def score_history_for_user(
        self, user_id: uuid.UUID, problem_id: uuid.UUID | None
    ) -> list[tuple[Score, ScoreBreakdown | None]]:
        stmt = select(Score).where(Score.user_id == user_id)
        if problem_id is not None:
            stmt = stmt.where(Score.problem_id == problem_id)
        stmt = stmt.order_by(Score.created_at.asc())
        scores = list(self.db.execute(stmt).scalars().all())
        return [(s, self.get_breakdown_for_score(s.id)) for s in scores]

    # --- Leaderboard aggregation ---

    def best_final_scores_for_hackathon(
        self, hackathon_id: uuid.UUID
    ) -> list[tuple[uuid.UUID, uuid.UUID, float, float]]:
        """Returns (user_id, problem_id, best_final_score, difficulty_multiplier)
        — the best ScoreBreakdown.final_score per user+problem within the
        given hackathon."""
        stmt = (
            select(
                Score.user_id,
                Score.problem_id,
                func.max(ScoreBreakdown.final_score),
                func.max(Problem.difficulty_multiplier),
            )
            .join(ScoreBreakdown, ScoreBreakdown.score_id == Score.id)
            .join(Problem, Problem.id == Score.problem_id)
            .where(Problem.hackathon_id == hackathon_id)
            .group_by(Score.user_id, Score.problem_id)
        )
        return list(self.db.execute(stmt).all())

    def get_student_names(self, user_ids: list[uuid.UUID]) -> dict[uuid.UUID, str]:
        if not user_ids:
            return {}
        stmt = select(User.id, User.full_name).where(User.id.in_(user_ids))
        return {row[0]: row[1] for row in self.db.execute(stmt).all()}

    def upsert_leaderboard_entry(
        self, hackathon_id: uuid.UUID, user_id: uuid.UUID, total_score: float, rank: int
    ) -> LeaderboardEntry:
        stmt = select(LeaderboardEntry).where(
            LeaderboardEntry.hackathon_id == hackathon_id, LeaderboardEntry.user_id == user_id
        )
        entry = self.db.execute(stmt).scalar_one_or_none()
        if entry is None:
            entry = LeaderboardEntry(
                hackathon_id=hackathon_id, user_id=user_id, total_score=total_score, rank=rank
            )
            self.db.add(entry)
        else:
            entry.total_score = total_score
            entry.rank = rank
        return entry

    def list_leaderboard(self, hackathon_id: uuid.UUID) -> list[LeaderboardEntry]:
        stmt = (
            select(LeaderboardEntry)
            .where(LeaderboardEntry.hackathon_id == hackathon_id)
            .order_by(LeaderboardEntry.rank.asc())
        )
        return list(self.db.execute(stmt).scalars().all())

    def commit(self) -> None:
        self.db.commit()
