from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Hackathon, Problem, RoleName, Role, Score, Submission, SubmissionStatus, User, Violation


class AdminRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def count_students(self) -> int:
        stmt = (
            select(func.count())
            .select_from(User)
            .join(Role, User.role_id == Role.id)
            .where(Role.name == RoleName.STUDENT.value)
        )
        return self.db.execute(stmt).scalar_one()

    def count_problems(self) -> int:
        return self.db.execute(select(func.count()).select_from(Problem)).scalar_one()

    def count_submissions(self) -> int:
        return self.db.execute(select(func.count()).select_from(Submission)).scalar_one()

    def count_violations(self) -> int:
        return self.db.execute(select(func.count()).select_from(Violation)).scalar_one()

    def get_active_hackathon(self) -> Hackathon | None:
        stmt = (
            select(Hackathon)
            .where(Hackathon.is_active.is_(True))
            .order_by(Hackathon.created_at.desc())
        )
        return self.db.execute(stmt).scalars().first()

    def count_problems_for_hackathon(self, hackathon_id) -> int:
        stmt = select(func.count()).select_from(Problem).where(Problem.hackathon_id == hackathon_id)
        return self.db.execute(stmt).scalar_one()

    def submission_status_counts(self) -> dict[str, int]:
        stmt = select(Submission.status, func.count()).group_by(Submission.status)
        rows = self.db.execute(stmt).all()
        counts = {status.value: 0 for status in SubmissionStatus}
        for status_value, count in rows:
            key = status_value.value if hasattr(status_value, "value") else status_value
            counts[key] = count
        return counts

    def top_scores(self, limit: int = 5) -> list[tuple[User, float]]:
        stmt = (
            select(User, func.sum(Score.points).label("total_points"))
            .join(Score, Score.user_id == User.id)
            .group_by(User.id)
            .order_by(func.sum(Score.points).desc())
            .limit(limit)
        )
        return [(row[0], float(row[1] or 0)) for row in self.db.execute(stmt).all()]
