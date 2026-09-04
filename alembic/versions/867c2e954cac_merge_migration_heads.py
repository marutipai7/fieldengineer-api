"""merge migration heads

Revision ID: 867c2e954cac
Revises: 8abb50857d60, 9ae0d7e2c074
Create Date: 2026-09-04 11:59:58.072304

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '867c2e954cac'
down_revision: Union[str, Sequence[str], None] = ('8abb50857d60', '9ae0d7e2c074')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
