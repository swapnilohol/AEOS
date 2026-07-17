"""create editor module tables

Revision ID: 0004
Revises: 0003
Create Date: 2026-07-11

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "code_drafts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("problem_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("problems.id"), nullable=False),
        sa.Column("language", sa.String(length=50), nullable=False, server_default="python"),
        sa.Column("code", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "problem_id", name="uq_code_drafts_user_problem"),
    )
    op.create_index("ix_code_drafts_user_id", "code_drafts", ["user_id"])
    op.create_index("ix_code_drafts_problem_id", "code_drafts", ["problem_id"])

    editor_session_status = postgresql.ENUM(
        "ACTIVE", "ENDED", name="editor_session_status"
    )
    editor_session_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "editor_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("problem_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("problems.id"), nullable=False),
        sa.Column("language", sa.String(length=50), nullable=False, server_default="python"),
        sa.Column("status", editor_session_status, nullable=False, server_default="ACTIVE"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_active_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_editor_sessions_user_id", "editor_sessions", ["user_id"])
    op.create_index("ix_editor_sessions_problem_id", "editor_sessions", ["problem_id"])


def downgrade() -> None:
    op.drop_table("editor_sessions")
    postgresql.ENUM(name="editor_session_status").drop(op.get_bind(), checkfirst=True)
    op.drop_table("code_drafts")
