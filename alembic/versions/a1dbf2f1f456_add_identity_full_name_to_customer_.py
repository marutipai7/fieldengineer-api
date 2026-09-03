"""add identity full name to customer identity

Revision ID: a1dbf2f1f456
Revises: 9dd1040164f4
Create Date: 2026-09-03 15:08:23.210413

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1dbf2f1f456'
down_revision: Union[str, Sequence[str], None] = '9dd1040164f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "customer_identities",
        sa.Column("identity_full_name", sa.String(length=255), nullable=True)
    )


def downgrade() -> None:
    op.drop_column(
        "customer_identities",
        "identity_full_name"
    )