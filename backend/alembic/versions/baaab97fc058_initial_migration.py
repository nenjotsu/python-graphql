"""Initial migration

Revision ID: baaab97fc058
Revises: b12fd08e6bbf
Create Date: 2025-11-14 23:39:37.120504

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'baaab97fc058'
down_revision: Union[str, Sequence[str], None] = 'b12fd08e6bbf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
