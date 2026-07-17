from sqlalchemy.orm import Session

from app.repositories.admin_repository import AdminRepository
from app.schemas.admin import (
    ActiveHackathonSummary,
    AdminDashboardResponse,
    SubmissionStatusBreakdown,
    TopScoreEntry,
)


class AdminService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = AdminRepository(db)

    def get_dashboard(self) -> AdminDashboardResponse:
        active_hackathon = self.repo.get_active_hackathon()
        active_hackathon_summary = None
        if active_hackathon is not None:
            active_hackathon_summary = ActiveHackathonSummary(
                id=active_hackathon.id,
                title=active_hackathon.title,
                start_time=active_hackathon.start_time,
                end_time=active_hackathon.end_time,
                problem_count=self.repo.count_problems_for_hackathon(active_hackathon.id),
            )

        status_counts = self.repo.submission_status_counts()
        breakdown = SubmissionStatusBreakdown(
            pending=status_counts.get("PENDING", 0),
            running=status_counts.get("RUNNING", 0),
            completed=status_counts.get("COMPLETED", 0),
            failed=status_counts.get("FAILED", 0),
        )

        top_scores = [
            TopScoreEntry(user_id=user.id, full_name=user.full_name, total_points=points)
            for user, points in self.repo.top_scores()
        ]

        return AdminDashboardResponse(
            total_students=self.repo.count_students(),
            total_problems=self.repo.count_problems(),
            total_submissions=self.repo.count_submissions(),
            total_violations=self.repo.count_violations(),
            active_hackathon=active_hackathon_summary,
            submission_status_breakdown=breakdown,
            top_scores=top_scores,
        )
