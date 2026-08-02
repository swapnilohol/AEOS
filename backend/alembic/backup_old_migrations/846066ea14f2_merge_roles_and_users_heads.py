"""merge roles and users heads

Revision ID: 846066ea14f2
Revises: 412dfd15cbdc, bba0d6b566c0
Create Date: 2026-07-16 17:36:06.449964

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '846066ea14f2'
down_revision: Union[str, Sequence[str], None] = ('412dfd15cbdc', 'bba0d6b566c0')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
