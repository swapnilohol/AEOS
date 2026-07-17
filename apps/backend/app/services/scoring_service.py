import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import RoleName, User
from app.repositories.scoring_repository import ScoringRepository
from app.schemas.scoring import (
    LeaderboardEntryResponse,
    ScoreBreakdownResponse,
    ScoreHistoryEntry,
)
from app.services.activity_service import ActivityService
from app.services.leaderboard_engine import BestProblemScore, compute_weighted_total, rank_totals
from app.services.scoring_engine import (
    compute_final_score,
    compute_penalty_factor,
    compute_performance_factor,
)


class SubmissionNotFoundError(Exception):
    pass


class ScoreNotFoundError(Exception):
    pass


class AccessDeniedError(Exception):
    pass


class ScoringService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ScoringRepository(db)

    def calculate_for_submission(self, submission_id: uuid.UUID) -> ScoreBreakdownResponse:
        submission = self.repo.get_submission(submission_id)
        if submission is None:
            raise SubmissionNotFoundError()

        score = self.repo.get_score_for_submission(submission_id)
        if score is None:
            raise ScoreNotFoundError()

        problem = self.repo.get_problem(submission.problem_id)
        max_score = float(problem.max_score) if problem else score.max_points
        difficulty_multiplier = problem.difficulty_multiplier if problem else 1.0

        avg_time = self.repo.avg_execution_time_for_passed_tests(submission_id)
        performance_factor = compute_performance_factor(
            avg_time,
            target_ms=settings.performance_target_ms,
            max_penalty_ratio=settings.performance_max_penalty_ratio,
        )

        is_late = self._is_late_submission(submission.problem_id, submission.submitted_at)
        penalty_factor = compute_penalty_factor(
            is_late, late_penalty_ratio=settings.late_penalty_ratio
        )

        final_score = compute_final_score(
            score.points,
            performance_factor=performance_factor,
            penalty_factor=penalty_factor,
            max_score=max_score,
        )

        breakdown = self.repo.upsert_breakdown(
            score.id,
            functional_score=score.points,
            performance_factor=performance_factor,
            difficulty_multiplier=difficulty_multiplier,
            penalty_factor=penalty_factor,
            quality_score=None,
            final_score=final_score,
        )
        self.repo.commit()

        if problem is not None:
            self._recompute_leaderboard(problem.hackathon_id)

        ActivityService(self.db).log(
            submission.user_id,
            "SCORE_CALCULATED",
            {"submission_id": str(submission.id), "final_score": final_score},
        )

        return self._to_breakdown_response(breakdown, submission, score)

    def _is_late_submission(self, problem_id: uuid.UUID, submitted_at: datetime) -> bool:
        problem = self.repo.get_problem(problem_id)
        if problem is None:
            return False
        hackathon = self.repo.get_hackathon(problem.hackathon_id)
        if hackathon is None or hackathon.end_time is None:
            return False
        return submitted_at > hackathon.end_time

    def _recompute_leaderboard(self, hackathon_id: uuid.UUID) -> None:
        rows = self.repo.best_final_scores_for_hackathon(hackathon_id)

        totals_by_user: dict[uuid.UUID, list[BestProblemScore]] = {}
        for user_id, problem_id, best_final_score, difficulty_multiplier in rows:
            totals_by_user.setdefault(user_id, []).append(
                BestProblemScore(
                    problem_id=str(problem_id),
                    best_final_score=float(best_final_score),
                    difficulty_multiplier=float(difficulty_multiplier),
                )
            )

        user_totals = [
            (str(user_id), compute_weighted_total(scores))
            for user_id, scores in totals_by_user.items()
        ]
        ranks = rank_totals(user_totals)

        for user_id_str, total in user_totals:
            user_id = uuid.UUID(user_id_str)
            self.repo.upsert_leaderboard_entry(
                hackathon_id=hackathon_id,
                user_id=user_id,
                total_score=total,
                rank=ranks[user_id_str],
            )
        self.repo.commit()

    def get_leaderboard(self, hackathon_id: uuid.UUID) -> list[LeaderboardEntryResponse]:
        entries = self.repo.list_leaderboard(hackathon_id)
        names = self.repo.get_student_names([e.user_id for e in entries])
        return [
            LeaderboardEntryResponse(
                rank=e.rank or 0,
                user_id=e.user_id,
                full_name=names.get(e.user_id, "Unknown"),
                total_score=e.total_score,
            )
            for e in entries
        ]

    def get_breakdown(
        self, current_user: User, submission_id: uuid.UUID
    ) -> ScoreBreakdownResponse:
        submission = self.repo.get_submission(submission_id)
        if submission is None:
            raise SubmissionNotFoundError()
        self._assert_can_view(current_user, submission.user_id)

        score = self.repo.get_score_for_submission(submission_id)
        if score is None:
            raise ScoreNotFoundError()
        breakdown = self.repo.get_breakdown_for_score(score.id)
        if breakdown is None:
            raise ScoreNotFoundError()
        return self._to_breakdown_response(breakdown, submission, score)

    def get_history(
        self, current_user: User, target_user_id: uuid.UUID, problem_id: uuid.UUID | None
    ) -> list[ScoreHistoryEntry]:
        self._assert_can_view(current_user, target_user_id)

        rows = self.repo.score_history_for_user(target_user_id, problem_id)
        entries = []
        for score, breakdown in rows:
            submission = self.repo.get_submission(score.submission_id)
            entries.append(
                ScoreHistoryEntry(
                    submission_id=score.submission_id,
                    problem_id=score.problem_id,
                    final_score=breakdown.final_score if breakdown else None,
                    max_points=score.max_points,
                    submitted_at=submission.submitted_at if submission else score.created_at,
                )
            )
        return entries

    def _assert_can_view(self, current_user: User, owner_id: uuid.UUID) -> None:
        is_admin = current_user.role.name == RoleName.ADMIN.value
        if not is_admin and current_user.id != owner_id:
            raise AccessDeniedError()

    def _to_breakdown_response(self, breakdown, submission, score) -> ScoreBreakdownResponse:
        return ScoreBreakdownResponse(
            score_id=breakdown.score_id,
            submission_id=submission.id,
            problem_id=submission.problem_id,
            functional_score=breakdown.functional_score,
            performance_factor=breakdown.performance_factor,
            difficulty_multiplier=breakdown.difficulty_multiplier,
            penalty_factor=breakdown.penalty_factor,
            quality_score=breakdown.quality_score,
            final_score=breakdown.final_score,
            max_points=score.max_points,
            computed_at=breakdown.updated_at,
        )
