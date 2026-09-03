"""add address on id to customer identity

Revision ID: 533db423a92a
Revises: 51830d522dbb
Create Date: 2026-09-03 13:35:25.987371

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '533db423a92a'
down_revision: Union[str, Sequence[str], None] = '51830d522dbb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "customer_identities",
        sa.Column("address_on_id", sa.Text(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column(
        "customer_identities",
        "address_on_id"
    )
    # ### end Alembic commands ###
