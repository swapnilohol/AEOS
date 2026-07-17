import uuid

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Problem(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "problems"

    hackathon_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hackathons.id"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    max_score: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    # Scoring Module: weights this problem's contribution to a student's
    # aggregate leaderboard total (does NOT scale the per-submission score,
    # which always stays within [0, max_score] — see docs/README.md).
    difficulty_multiplier: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
