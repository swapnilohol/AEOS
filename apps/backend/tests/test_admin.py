import uuid
from datetime import datetime, timezone

from app.schemas.admin import (
    ActiveHackathonSummary,
    AdminDashboardResponse,
    SubmissionStatusBreakdown,
    TopScoreEntry,
)


def test_admin_dashboard_response_with_active_hackathon() -> None:
    hackathon = ActiveHackathonSummary(
        id=uuid.uuid4(),
        title="AI Elite Internship Hackathon",
        start_time=datetime.now(timezone.utc),
        end_time=None,
        problem_count=4,
    )
    breakdown = SubmissionStatusBreakdown(pending=1, running=0, completed=3, failed=0)
    top_scores = [
        TopScoreEntry(user_id=uuid.uuid4(), full_name="Ada Lovelace", total_points=95.0)
    ]

    dashboard = AdminDashboardResponse(
        total_students=10,
        total_problems=4,
        total_submissions=4,
        total_violations=0,
        active_hackathon=hackathon,
        submission_status_breakdown=breakdown,
        top_scores=top_scores,
    )

    assert dashboard.active_hackathon.problem_count == 4
    assert dashboard.submission_status_breakdown.completed == 3
    assert dashboard.top_scores[0].full_name == "Ada Lovelace"


def test_admin_dashboard_response_without_active_hackathon() -> None:
    breakdown = SubmissionStatusBreakdown(pending=0, running=0, completed=0, failed=0)

    dashboard = AdminDashboardResponse(
        total_students=0,
        total_problems=0,
        total_submissions=0,
        total_violations=0,
        active_hackathon=None,
        submission_status_breakdown=breakdown,
        top_scores=[],
    )

    assert dashboard.active_hackathon is None
    assert dashboard.top_scores == []
