import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models import Hackathon, Problem, Score, StudentProfile, Submission, User


class StudentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, profile_id: uuid.UUID) -> StudentProfile | None:
        return self.db.get(StudentProfile, profile_id)

    def get_by_user_id(self, user_id: uuid.UUID) -> StudentProfile | None:
        stmt = select(StudentProfile).where(StudentProfile.user_id == user_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_student_id(self, student_id: str) -> StudentProfile | None:
        stmt = select(StudentProfile).where(StudentProfile.student_id == student_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def list_students(
        self, *, search: str | None, page: int, page_size: int
    ) -> tuple[list[StudentProfile], int]:
        stmt = select(StudentProfile).join(User, StudentProfile.user_id == User.id)
        count_stmt = select(func.count()).select_from(StudentProfile).join(
            User, StudentProfile.user_id == User.id
        )

        if search:
            like = f"%{search}%"
            condition = or_(
                User.full_name.ilike(like),
                User.email.ilike(like),
                StudentProfile.student_id.ilike(like),
            )
            stmt = stmt.where(condition)
            count_stmt = count_stmt.where(condition)

        total = self.db.execute(count_stmt).scalar_one()
        stmt = stmt.order_by(StudentProfile.created_at.desc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        items = list(self.db.execute(stmt).scalars().all())
        return items, total

    def create_profile(self, user_id: uuid.UUID, **fields) -> StudentProfile:
        profile = StudentProfile(user_id=user_id, **fields)
        self.db.add(profile)
        self.db.flush()
        return profile

    def delete(self, profile: StudentProfile) -> None:
        self.db.delete(profile)

    def count_submissions_for_user(self, user_id: uuid.UUID) -> int:
        stmt = select(func.count()).select_from(Submission).where(Submission.user_id == user_id)
        return self.db.execute(stmt).scalar_one()

    def count_active_hackathon_problems(self) -> int:
        stmt = (
            select(func.count())
            .select_from(Problem)
            .join(Hackathon, Problem.hackathon_id == Hackathon.id)
            .where(Hackathon.is_active.is_(True))
        )
        return self.db.execute(stmt).scalar_one()

    def best_score_for_user(self, user_id: uuid.UUID) -> float | None:
        stmt = select(func.max(Score.points)).where(Score.user_id == user_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def commit(self) -> None:
        self.db.commit()

    def refresh(self, profile: StudentProfile) -> None:
        self.db.refresh(profile)
