import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.queue import enqueue_submission
from app.models import User
from app.repositories.admin_repository import AdminRepository
from app.repositories.editor_repository import EditorRepository
from app.repositories.problem_repository import ProblemRepository
from app.schemas.editor import ProblemSummary, SaveDraftRequest, SubmitSolutionRequest
from app.services.activity_service import ActivityService


class ProblemNotFoundError(Exception):
    pass


class DraftNotFoundError(Exception):
    pass


class SessionNotFoundError(Exception):
    pass


class SessionNotOwnedError(Exception):
    pass


class NoDraftToSubmitError(Exception):
    pass


class EditorService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = EditorRepository(db)
        self.problem_repo = ProblemRepository(db)
        self.admin_repo = AdminRepository(db)

    def _require_problem(self, problem_id: uuid.UUID):
        problem = self.problem_repo.get_by_id(problem_id)
        if problem is None:
            raise ProblemNotFoundError()
        return problem

    def save_draft(self, user: User, problem_id: uuid.UUID, payload: SaveDraftRequest):
        self._require_problem(problem_id)
        draft = self.repo.upsert_draft(
            user_id=user.id, problem_id=problem_id, language=payload.language, code=payload.code
        )
        self.repo.commit()
        self.repo.refresh(draft)
        return draft

    def get_draft(self, user: User, problem_id: uuid.UUID):
        self._require_problem(problem_id)
        draft = self.repo.get_draft(user.id, problem_id)
        if draft is None:
            raise DraftNotFoundError()
        return draft

    def start_session(self, user: User, problem_id: uuid.UUID, language: str):
        self._require_problem(problem_id)
        existing = self.repo.get_active_session(user.id, problem_id)
        if existing is not None:
            return existing
        session = self.repo.create_session(user_id=user.id, problem_id=problem_id, language=language)
        self.repo.commit()
        self.repo.refresh(session)
        return session

    def heartbeat_session(self, user: User, session_id: uuid.UUID):
        session = self.repo.get_session_by_id(session_id)
        if session is None:
            raise SessionNotFoundError()
        if session.user_id != user.id:
            raise SessionNotOwnedError()
        self.repo.touch_session(session)
        self.repo.commit()
        self.repo.refresh(session)
        return session

    def end_session(self, user: User, session_id: uuid.UUID):
        session = self.repo.get_session_by_id(session_id)
        if session is None:
            raise SessionNotFoundError()
        if session.user_id != user.id:
            raise SessionNotOwnedError()
        self.repo.end_session(session)
        self.repo.commit()
        self.repo.refresh(session)
        return session

    def list_active_sessions_for_admin(self):
        return self.repo.list_active_sessions()

    def submit_solution(self, user: User, problem_id: uuid.UUID, payload: SubmitSolutionRequest):
        self._require_problem(problem_id)

        code = payload.code
        language = payload.language
        if code is None or language is None:
            draft = self.repo.get_draft(user.id, problem_id)
            if draft is None:
                raise NoDraftToSubmitError()
            code = code if code is not None else draft.code
            language = language if language is not None else draft.language

        submission = self.repo.create_submission(
            user_id=user.id, problem_id=problem_id, code=code, language=language
        )

        active_session = self.repo.get_active_session(user.id, problem_id)
        if active_session is not None:
            self.repo.touch_session(active_session)

        self.repo.commit()
        self.repo.refresh(submission)
        enqueue_submission(str(submission.id))
        ActivityService(self.db).log(
            user.id, "SUBMISSION_CREATED", {"problem_id": str(problem_id)}
        )
        return submission

    def get_workspace(self, user: User, problem_id: uuid.UUID):
        problem = self._require_problem(problem_id)

        draft = self.repo.get_draft(user.id, problem_id)
        active_session = self.repo.get_active_session(user.id, problem_id)
        latest_submission = self.repo.get_latest_submission(user.id, problem_id)

        remaining_seconds = None
        active_hackathon = self.admin_repo.get_active_hackathon()
        if active_hackathon is not None and active_hackathon.end_time is not None:
            delta = (active_hackathon.end_time - datetime.now(timezone.utc)).total_seconds()
            remaining_seconds = max(0, int(delta))

        problem_summary = ProblemSummary(
            id=problem.id,
            title=problem.title,
            description=problem.description,
            max_score=problem.max_score,
        )

        return {
            "problem": problem_summary,
            "student_full_name": user.full_name,
            "remaining_seconds": remaining_seconds,
            "draft": draft,
            "active_session": active_session,
            "latest_submission_status": (
                latest_submission.status.value if latest_submission else None
            ),
        }
