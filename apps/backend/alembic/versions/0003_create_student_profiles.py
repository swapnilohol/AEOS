"""create student_profiles table

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-11

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "student_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
            unique=True,
        ),
        sa.Column("student_id", sa.String(length=50), nullable=False, unique=True),
        sa.Column("college_name", sa.String(length=255), nullable=True),
        sa.Column("department", sa.String(length=255), nullable=True),
        sa.Column("semester", sa.Integer(), nullable=True),
        sa.Column("graduation_year", sa.Integer(), nullable=True),
        sa.Column("phone_number", sa.String(length=20), nullable=True),
        sa.Column("skills", sa.Text(), nullable=True),
        sa.Column("resume_url", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_student_profiles_user_id", "student_profiles", ["user_id"])
    op.create_index("ix_student_profiles_student_id", "student_profiles", ["student_id"])


def downgrade() -> None:
    op.drop_table("student_profiles")
