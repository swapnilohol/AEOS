import uuid

from sqlalchemy.orm import Session

from app.models import RoleName, User
from app.repositories.submission_repository import SubmissionRepository


class SubmissionNotFoundError(Exception):
    pass


class SubmissionAccessDeniedError(Exception):
    pass


class SubmissionService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = SubmissionRepository(db)

    def get_submission(self, current_user: User, submission_id: uuid.UUID):
        submission = self.repo.get_by_id(submission_id)
        if submission is None:
            raise SubmissionNotFoundError()
        self._assert_can_view(current_user, submission.user_id)
        return submission

    def list_my_submissions(self, current_user: User, problem_id: uuid.UUID | None):
        return self.repo.list_for_user(current_user.id, problem_id=problem_id)

    def get_results(self, current_user: User, submission_id: uuid.UUID):
        submission = self.repo.get_by_id(submission_id)
        if submission is None:
            raise SubmissionNotFoundError()
        self._assert_can_view(current_user, submission.user_id)

        is_admin = current_user.role.name == RoleName.ADMIN.value
        results = self.repo.list_results_with_visibility(submission_id)

        response_rows = []
        for result, is_hidden in results:
            redact = is_hidden and not is_admin
            response_rows.append(
                {
                    "id": result.id,
                    "problem_test_id": result.problem_test_id,
                    "is_hidden": is_hidden,
                    "passed": result.passed,
                    "execution_time_ms": result.execution_time_ms,
                    "actual_output": None if redact else result.actual_output,
                    "error_message": None if redact else result.error_message,
                }
            )
        return response_rows

    def _assert_can_view(self, current_user: User, owner_id: uuid.UUID) -> None:
        is_admin = current_user.role.name == RoleName.ADMIN.value
        if not is_admin and current_user.id != owner_id:
            raise SubmissionAccessDeniedError()
