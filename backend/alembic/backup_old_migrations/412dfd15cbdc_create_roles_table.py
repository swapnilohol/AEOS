"""create roles table

Revision ID: 412dfd15cbdc
Revises: 1f0e1f685616
Create Date: 2026-07-16
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "412dfd15cbdc"
down_revision: Union[str, Sequence[str], None] = "1f0e1f685616"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "roles",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True
        ),
        sa.Column(
            "name",
            sa.String(),
            unique=True,
            nullable=False
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now()
        ),
    )


def downgrade() -> None:
    op.drop_table("roles")
