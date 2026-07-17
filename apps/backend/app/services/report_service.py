import uuid

from sqlalchemy.orm import Session

from app.models import Hackathon
from app.repositories.admin_repository import AdminRepository
from app.repositories.dashboard_repository import DashboardRepository
from app.repositories.scoring_repository import ScoringRepository
from app.repositories.student_repository import StudentRepository
from app.repositories.submission_repository import SubmissionRepository


class StudentNotFoundForReportError(Exception):
    pass


class ReportService:
    """Produces structured JSON report data (Global Rule: avoid complex BI
    systems / overengineering). Exporting to PDF/CSV is a natural future
    extension, not implemented here."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.dashboard_repo = DashboardRepository(db)
        self.admin_repo = AdminRepository(db)
        self.scoring_repo = ScoringRepository(db)
        self.student_repo = StudentRepository(db)
        self.submission_repo = SubmissionRepository(db)

    def student_report(self, user_id: uuid.UUID) -> dict:
        profile = self.student_repo.get_by_user_id(user_id)
        if profile is None:
            raise StudentNotFoundForReportError()

        _submissions, total = self.submission_repo.list_for_user(user_id, problem_id=None)
        history = self.scoring_repo.score_history_for_user(user_id, problem_id=None)

        return {
            "student": {
                "user_id": profile.user_id,
                "full_name": profile.user.full_name,
                "student_id": profile.student_id,
                "college_name": profile.college_name,
                "department": profile.department,
                "semester": profile.semester,
            },
            "total_submissions": total,
            "score_history": [
                {
                    "submission_id": score.submission_id,
                    "problem_id": score.problem_id,
                    "final_score": breakdown.final_score if breakdown else None,
                    "max_points": score.max_points,
                }
                for score, breakdown in history
            ],
        }

    def submission_report(self) -> dict:
        total_students = self.dashboard_repo.total_students()
        return {
            "total_students": total_students,
            "submission_status_breakdown": self.admin_repo.submission_status_counts(),
            "problem_completion": self.dashboard_repo.problem_completion_rates(total_students),
            "score_distribution": self.dashboard_repo.score_distribution(),
        }

    def hackathon_summary(self, hackathon_id: uuid.UUID | None) -> dict:
        hackathon = (
            self.db.get(Hackathon, hackathon_id)
            if hackathon_id
            else self.admin_repo.get_active_hackathon()
        )
        if hackathon is None:
            return {"hackathon": None}

        return {
            "hackathon": {
                "id": hackathon.id,
                "title": hackathon.title,
                "start_time": hackathon.start_time,
                "end_time": hackathon.end_time,
                "is_active": hackathon.is_active,
            },
            "total_problems": self.admin_repo.count_problems_for_hackathon(hackathon.id),
            "leaderboard": self.scoring_repo.list_leaderboard(hackathon.id),
        }
