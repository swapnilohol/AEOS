import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ActivityLog


class ActivityRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, user_id: uuid.UUID, activity_type: str, metadata_json: str | None) -> ActivityLog:
        entry = ActivityLog(user_id=user_id, activity_type=activity_type, metadata_json=metadata_json)
        self.db.add(entry)
        self.db.flush()
        return entry

    def list_recent(self, limit: int = 20) -> list[ActivityLog]:
        stmt = select(ActivityLog).order_by(ActivityLog.created_at.desc()).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def commit(self) -> None:
        self.db.commit()
