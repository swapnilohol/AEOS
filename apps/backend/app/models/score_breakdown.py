import uuid

from sqlalchemy import Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class ScoreBreakdown(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """One breakdown per Score (1:1). `created_at` doubles as the score
    history timeline: each Submission has its own Score/ScoreBreakdown row,
    so a user's history for a problem is just these rows ordered by time —
    no separate history table needed."""

    __tablename__ = "score_breakdowns"

    score_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("scores.id"), nullable=False, unique=True, index=True
    )
    functional_score: Mapped[float] = mapped_column(Float, nullable=False)
    performance_factor: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    difficulty_multiplier: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    penalty_factor: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    final_score: Mapped[float] = mapped_column(Float, nullable=False)
