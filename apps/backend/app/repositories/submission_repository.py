import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import ExecutionResult, ProblemTest, Submission


class SubmissionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, submission_id: uuid.UUID) -> Submission | None:
        return self.db.get(Submission, submission_id)

    def list_for_user(
        self, user_id: uuid.UUID, *, problem_id: uuid.UUID | None
    ) -> tuple[list[Submission], int]:
        stmt = select(Submission).where(Submission.user_id == user_id)
        count_stmt = select(func.count()).select_from(Submission).where(Submission.user_id == user_id)

        if problem_id is not None:
            stmt = stmt.where(Submission.problem_id == problem_id)
            count_stmt = count_stmt.where(Submission.problem_id == problem_id)

        stmt = stmt.order_by(Submission.submitted_at.desc())
        total = self.db.execute(count_stmt).scalar_one()
        items = list(self.db.execute(stmt).scalars().all())
        return items, total

    def list_results_with_visibility(
        self, submission_id: uuid.UUID
    ) -> list[tuple[ExecutionResult, bool]]:
        """Returns (result, is_hidden) pairs so the API layer can redact
        hidden-test details for non-admin viewers."""
        stmt = (
            select(ExecutionResult, ProblemTest.is_hidden)
            .join(ProblemTest, ExecutionResult.problem_test_id == ProblemTest.id)
            .where(ExecutionResult.submission_id == submission_id)
        )
        return [(row[0], row[1]) for row in self.db.execute(stmt).all()]
