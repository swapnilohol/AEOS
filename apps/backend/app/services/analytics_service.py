import uuid

from sqlalchemy.orm import Session

from app.repositories.admin_repository import AdminRepository
from app.repositories.dashboard_repository import DashboardRepository
from app.repositories.scoring_repository import ScoringRepository
from app.repositories.student_repository import StudentRepository


class AnalyticsService:
    """Calculates dashboard metrics. Reuses AdminRepository (Admin Module),
    ScoringRepository (Scoring Module), and StudentRepository (Student
    Management Module) rather than re-querying the same data, per the
    Global Rule against duplicated logic. DashboardRepository holds only
    the genuinely new queries this module needs."""

    def __init__(self, db: Session) -> None:
        self.dashboard_repo = DashboardRepository(db)
        self.admin_repo = AdminRepository(db)
        self.scoring_repo = ScoringRepository(db)
        self.student_repo = StudentRepository(db)

    def admin_overview(self) -> dict:
        total_students = self.dashboard_repo.total_students()
        return {
            "total_students": total_students,
            "active_students": self.dashboard_repo.count_active_students(),
            "total_problems": self.admin_repo.count_problems(),
            "total_submissions": self.admin_repo.count_submissions(),
            "completed_assessments": self.dashboard_repo.count_completed_assessments(),
            "average_score": self.dashboard_repo.average_final_score(),
            "active_hackathon": self.admin_repo.get_active_hackathon(),
        }

    def admin_live_status(self) -> dict:
        status_counts = self.admin_repo.submission_status_counts()
        return {
            "active_students": self.dashboard_repo.count_active_students(),
            "running_executions": status_counts.get("RUNNING", 0),
            "completed_submissions": status_counts.get("COMPLETED", 0),
            "failed_executions": status_counts.get("FAILED", 0),
        }

    def admin_analytics(self) -> dict:
        total_students = self.dashboard_repo.total_students()
        return {
            "average_score": self.dashboard_repo.average_final_score(),
            "problem_completion": self.dashboard_repo.problem_completion_rates(total_students),
            "score_distribution": self.dashboard_repo.score_distribution(),
            "execution_stats": {
                "timeout_count": self.dashboard_repo.timeout_count(),
                "failed_executions": self.dashboard_repo.failed_executions_count(),
                "average_execution_time_ms": self.dashboard_repo.average_execution_time_ms(),
            },
        }

    def student_progress(self, user_id: uuid.UUID) -> dict:
        counts = self.dashboard_repo.student_submission_counts(user_id)
        total_problems = self.student_repo.count_active_hackathon_problems()
        completion_percent = (
            round(counts["solved"] / total_problems * 100, 1) if total_problems else 0.0
        )
        return {
            "problems_attempted": counts["attempted"],
            "problems_solved": counts["solved"],
            "total_problems": total_problems,
            "completion_percent": completion_percent,
        }

    def student_rank(self, hackathon_id: uuid.UUID, user_id: uuid.UUID) -> dict | None:
        entries = self.scoring_repo.list_leaderboard(hackathon_id)
        for entry in entries:
            if entry.user_id == user_id:
                return {
                    "rank": entry.rank,
                    "total_score": entry.total_score,
                    "total_participants": len(entries),
                }
        return None
