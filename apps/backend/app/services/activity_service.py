import json
import uuid

from sqlalchemy.orm import Session

from app.repositories.activity_repository import ActivityRepository


class ActivityService:
    """Deliberately tiny and dependency-free (only needs a DB session) so
    it can be imported from other services (Auth, Editor, Scoring) without
    pulling in the rest of the Dashboard Module."""

    def __init__(self, db: Session) -> None:
        self.repo = ActivityRepository(db)

    def log(self, user_id: uuid.UUID, activity_type: str, metadata: dict | None = None) -> None:
        metadata_json = json.dumps(metadata) if metadata else None
        self.repo.create(user_id, activity_type, metadata_json)
        self.repo.commit()

    def list_recent(self, limit: int = 20) -> list[dict]:
        entries = self.repo.list_recent(limit)
        return [
            {
                "id": e.id,
                "user_id": e.user_id,
                "activity_type": e.activity_type,
                "metadata": json.loads(e.metadata_json) if e.metadata_json else None,
                "created_at": e.created_at,
            }
            for e in entries
        ]
