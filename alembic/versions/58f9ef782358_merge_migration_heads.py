"""merge migration heads

Revision ID: 58f9ef782358
Revises: 2aa03f6b5f0c, 8abb50857d60
Create Date: 2026-09-04 15:17:49.398225

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '58f9ef782358'
down_revision: Union[str, Sequence[str], None] = ('2aa03f6b5f0c', '8abb50857d60')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
