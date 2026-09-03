"""add icon to services

Revision ID: 2a806e3d16cd
Revises: a82f1285505e
Create Date: 2026-09-03 16:27:55.047015

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2a806e3d16cd'
down_revision: Union[str, Sequence[str], None] = 'a82f1285505e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "services",
        sa.Column(
            "icon",
            sa.String(length=100),
            nullable=True
        )
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column(
        "services",
        "icon"
    )
