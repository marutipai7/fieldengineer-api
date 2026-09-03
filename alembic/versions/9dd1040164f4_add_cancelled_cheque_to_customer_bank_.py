"""add cancelled cheque to customer bank detail

Revision ID: 9dd1040164f4
Revises: 533db423a92a
Create Date: 2026-09-03 14:11:21.498913

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '9dd1040164f4'
down_revision: Union[str, Sequence[str], None] = '533db423a92a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "customer_bank_details",
        sa.Column("cancelled_cheque", sa.String(length=500), nullable=True)
    )


def downgrade() -> None:
    op.drop_column(
        "customer_bank_details",
        "cancelled_cheque"
    )