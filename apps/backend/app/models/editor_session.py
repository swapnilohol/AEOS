import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class EditorSessionStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    ENDED = "ENDED"


class EditorSession(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A temporary coding workspace session, opened when a student starts
    working on a problem. Conceptually this is the "EDITOR_SESSION"
    workspace entity described in the Editor Module prompt — it is a
    resource/session record, not an authentication role, and is therefore
    not added to the `roles` table used by RBAC."""

    __tablename__ = "editor_sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    problem_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("problems.id"), nullable=False, index=True
    )
    language: Mapped[str] = mapped_column(String(50), default="python", nullable=False)
    status: Mapped[EditorSessionStatus] = mapped_column(
        Enum(EditorSessionStatus, name="editor_session_status"),
        default=EditorSessionStatus.ACTIVE,
        nullable=False,
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_active_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
