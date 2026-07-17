import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import UUIDPrimaryKeyMixin


class ActivityLog(UUIDPrimaryKeyMixin, Base):
    """Append-only log powering the dashboard's activity feed. No
    `updated_at` (events are immutable once recorded).

    NOTE: the prompt's field name `metadata` is a reserved attribute on
    SQLAlchemy's declarative Base (`Base.metadata` is the schema registry),
    so the column is named `metadata_json` here instead — a small, necessary
    deviation, documented in docs/README.md.
    """

    __tablename__ = "activity_logs"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    activity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
