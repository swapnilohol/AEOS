"""add difficulty multiplier and score breakdowns

Revision ID: 0005
Revises: 0004
Create Date: 2026-07-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "problems",
        sa.Column(
            "difficulty_multiplier", sa.Float(), nullable=False, server_default="1.0"
        ),
    )

    op.create_table(
        "score_breakdowns",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "score_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("scores.id"),
            nullable=False,
            unique=True,
        ),
        sa.Column("functional_score", sa.Float(), nullable=False),
        sa.Column("performance_factor", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("difficulty_multiplier", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("penalty_factor", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("quality_score", sa.Float(), nullable=True),
        sa.Column("final_score", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_score_breakdowns_score_id", "score_breakdowns", ["score_id"])


def downgrade() -> None:
    op.drop_table("score_breakdowns")
    op.drop_column("problems", "difficulty_multiplier")
