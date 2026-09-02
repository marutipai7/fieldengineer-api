"""merge existing migration heads

Revision ID: 503640006081
Revises: 45bc7ea044ee, a02a97909fd9, b5d8e9f0a1b2, c6f31fae002d
Create Date: 2026-09-02 13:47:32.532384

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '503640006081'
down_revision: Union[str, Sequence[str], None] = ('45bc7ea044ee', 'a02a97909fd9', 'b5d8e9f0a1b2', 'c6f31fae002d')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
