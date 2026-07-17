import uuid

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class CodeDraft(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "code_drafts"
    __table_args__ = (UniqueConstraint("user_id", "problem_id", name="uq_code_drafts_user_problem"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    problem_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("problems.id"), nullable=False, index=True
    )
    language: Mapped[str] = mapped_column(String(50), default="python", nullable=False)
    code: Mapped[str] = mapped_column(Text, nullable=False, default="")
