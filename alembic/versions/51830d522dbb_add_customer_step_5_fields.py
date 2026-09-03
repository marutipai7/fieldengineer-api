"""add customer step 5 fields

Revision ID: 51830d522dbb
Revises: f4c8b1a9d2e7
Create Date: 2026-09-03 13:20:56.346633

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '51830d522dbb'
down_revision: Union[str, Sequence[str], None] = 'f4c8b1a9d2e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "customer_documents",
        sa.Column("cin_number", sa.String(length=100), nullable=True)
    )
    op.add_column(
        "customer_documents",
        sa.Column("tax_number", sa.String(length=100), nullable=True)
    )
    op.add_column(
        "customer_documents",
        sa.Column("gst_number", sa.String(length=100), nullable=True)
    )
    op.add_column(
        "customer_documents",
        sa.Column("document_number", sa.String(length=100), nullable=True)
    )
    op.add_column(
        "customer_documents",
        sa.Column("bank_account_number", sa.String(length=100), nullable=True)
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    op.drop_column("customer_documents", "bank_account_number")
    op.drop_column("customer_documents", "document_number")
    op.drop_column("customer_documents", "gst_number")
    op.drop_column("customer_documents", "tax_number")
    op.drop_column("customer_documents", "cin_number")
    # ### end Alembic commands ###
