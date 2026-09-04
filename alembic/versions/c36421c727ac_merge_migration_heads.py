"""merge migration heads

Revision ID: c36421c727ac
Revises: 0a1e775debd0, 536fa7b1f2e6
Create Date: 2026-09-04 17:06:06.886665

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c36421c727ac'
down_revision: Union[str, Sequence[str], None] = ('0a1e775debd0', '536fa7b1f2e6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
