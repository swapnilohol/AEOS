import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.repositories.scoring_repository import ScoringRepository
from app.repositories.student_repository import StudentRepository
from app.services.activity_service import ActivityService
from app.services.analytics_service import AnalyticsService
from app.services.report_service import ReportService, StudentNotFoundForReportError


class DashboardDataUnavailableError(Exception):
    pass


class StudentProfileRequiredError(Exception):
    pass


class ReportGenerationFailedError(Exception):
    pass


class DashboardService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.analytics = AnalyticsService(db)
        self.reports = ReportService(db)
        self.activity = ActivityService(db)
        self.scoring_repo = ScoringRepository(db)
        self.student_repo = StudentRepository(db)

    # --- Admin ---

    def get_admin_overview(self) -> dict:
        overview = self.analytics.admin_overview()
        live_status = self.analytics.admin_live_status()
        hackathon = overview.pop("active_hackathon", None)

        return {
            **overview,
            "live_status": live_status,
            "active_hackathon": (
                {
                    "id": hackathon.id,
                    "title": hackathon.title,
                    "start_time": hackathon.start_time,
                    "end_time": hackathon.end_time,
                }
                if hackathon
                else None
            ),
        }

    def get_admin_analytics(self) -> dict:
        return self.analytics.admin_analytics()

    def get_admin_activity(self, limit: int = 20) -> list[dict]:
        return self.activity.list_recent(limit)

    def get_student_report(self, user_id: uuid.UUID) -> dict:
        try:
            return self.reports.student_report(user_id)
        except StudentNotFoundForReportError:
            raise DashboardDataUnavailableError("No student profile found for that user")

    def get_submission_report(self) -> dict:
        return self.reports.submission_report()

    def get_hackathon_summary(self, hackathon_id: uuid.UUID | None) -> dict:
        return self.reports.hackathon_summary(hackathon_id)

    # --- Student ---

    def get_student_overview(self, user) -> dict:
        profile = self.student_repo.get_by_user_id(user.id)
        if profile is None:
            raise StudentProfileRequiredError()

        active_hackathon_repo = self.analytics.admin_repo.get_active_hackathon()
        remaining_seconds = None
        if active_hackathon_repo is not None and active_hackathon_repo.end_time is not None:
            delta = (active_hackathon_repo.end_time - datetime.now(timezone.utc)).total_seconds()
            remaining_seconds = max(0, int(delta))

        progress = self.analytics.student_progress(user.id)
        rank_info = (
            self.analytics.student_rank(active_hackathon_repo.id, user.id)
            if active_hackathon_repo
            else None
        )

        return {
            "profile": {
                "full_name": user.full_name,
                "college_name": profile.college_name,
                "department": profile.department,
                "semester": profile.semester,
            },
            "hackathon_status": (
                "ACTIVE" if active_hackathon_repo and active_hackathon_repo.is_active else "NONE"
            ),
            "remaining_seconds": remaining_seconds,
            "progress": progress,
            "rank": rank_info,
        }

    def get_student_performance(self, user) -> dict:
        history = self.scoring_repo.score_history_for_user(user.id, problem_id=None)
        return {
            "score_history": [
                {
                    "submission_id": score.submission_id,
                    "problem_id": score.problem_id,
                    "final_score": breakdown.final_score if breakdown else None,
                    "max_points": score.max_points,
                    "achieved_at": score.created_at,
                }
                for score, breakdown in history
            ]
        }

    def get_student_leaderboard(self, user, hackathon_id: uuid.UUID | None) -> dict:
        active_hackathon = (
            self.analytics.admin_repo.get_active_hackathon() if hackathon_id is None else None
        )
        target_hackathon_id = hackathon_id or (active_hackathon.id if active_hackathon else None)
        if target_hackathon_id is None:
            raise DashboardDataUnavailableError("No active hackathon")

        entries = self.scoring_repo.list_leaderboard(target_hackathon_id)
        names = self.scoring_repo.get_student_names([e.user_id for e in entries])
        own_entry = next((e for e in entries if e.user_id == user.id), None)

        return {
            "hackathon_id": target_hackathon_id,
            "total_participants": len(entries),
            "own_rank": own_entry.rank if own_entry else None,
            "own_total_score": own_entry.total_score if own_entry else None,
            "top_entries": [
                {
                    "rank": e.rank,
                    "user_id": e.user_id,
                    "full_name": names.get(e.user_id, "Unknown"),
                    "total_score": e.total_score,
                }
                for e in entries[:10]
            ],
        }
