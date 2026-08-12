"""merge engineer invitation and notification branches

Revision ID: a02a97909fd9
Revises: b2c3d4e5f6a7, 85c41fbb1614
Create Date: 2026-08-12 17:24:15.329132

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a02a97909fd9'
down_revision: Union[str, Sequence[str], None] = ('b2c3d4e5f6a7', '85c41fbb1614')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
