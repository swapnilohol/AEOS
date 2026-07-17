import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import CodeDraft, EditorSession, EditorSessionStatus, Submission, SubmissionStatus


class EditorRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    # --- Drafts ---

    def get_draft(self, user_id: uuid.UUID, problem_id: uuid.UUID) -> CodeDraft | None:
        stmt = select(CodeDraft).where(
            CodeDraft.user_id == user_id, CodeDraft.problem_id == problem_id
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def upsert_draft(
        self, user_id: uuid.UUID, problem_id: uuid.UUID, language: str, code: str
    ) -> CodeDraft:
        draft = self.get_draft(user_id, problem_id)
        if draft is None:
            draft = CodeDraft(user_id=user_id, problem_id=problem_id, language=language, code=code)
            self.db.add(draft)
        else:
            draft.language = language
            draft.code = code
        self.db.flush()
        return draft

    # --- Sessions ---

    def get_active_session(self, user_id: uuid.UUID, problem_id: uuid.UUID) -> EditorSession | None:
        stmt = select(EditorSession).where(
            EditorSession.user_id == user_id,
            EditorSession.problem_id == problem_id,
            EditorSession.status == EditorSessionStatus.ACTIVE,
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_session_by_id(self, session_id: uuid.UUID) -> EditorSession | None:
        return self.db.get(EditorSession, session_id)

    def create_session(self, user_id: uuid.UUID, problem_id: uuid.UUID, language: str) -> EditorSession:
        now = datetime.now(timezone.utc)
        session = EditorSession(
            user_id=user_id,
            problem_id=problem_id,
            language=language,
            status=EditorSessionStatus.ACTIVE,
            started_at=now,
            last_active_at=now,
        )
        self.db.add(session)
        self.db.flush()
        return session

    def touch_session(self, session: EditorSession) -> None:
        session.last_active_at = datetime.now(timezone.utc)

    def end_session(self, session: EditorSession) -> None:
        session.status = EditorSessionStatus.ENDED
        session.ended_at = datetime.now(timezone.utc)

    def list_active_sessions(self) -> list[EditorSession]:
        stmt = select(EditorSession).where(EditorSession.status == EditorSessionStatus.ACTIVE)
        return list(self.db.execute(stmt).scalars().all())

    # --- Submissions (creation only; execution is out of scope here) ---

    def get_latest_submission(self, user_id: uuid.UUID, problem_id: uuid.UUID) -> Submission | None:
        stmt = (
            select(Submission)
            .where(Submission.user_id == user_id, Submission.problem_id == problem_id)
            .order_by(Submission.submitted_at.desc())
        )
        return self.db.execute(stmt).scalars().first()

    def create_submission(
        self, user_id: uuid.UUID, problem_id: uuid.UUID, code: str, language: str
    ) -> Submission:
        submission = Submission(
            user_id=user_id,
            problem_id=problem_id,
            code=code,
            language=language,
            status=SubmissionStatus.PENDING,
            submitted_at=datetime.now(timezone.utc),
        )
        self.db.add(submission)
        self.db.flush()
        return submission

    def commit(self) -> None:
        self.db.commit()

    def refresh(self, instance) -> None:
        self.db.refresh(instance)
