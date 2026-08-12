"""add receiver id to call sessions

Revision ID: 9b6e7e8f09b2
Revises: e100a0a66853
Create Date: 2026-08-12
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9b6e7e8f09b2"
down_revision: Union[str, Sequence[str], None] = "e100a0a66853"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "call_sessions",
        sa.Column("receiver_id", sa.Integer(), nullable=True),
    )

    op.create_foreign_key(
        "fk_call_sessions_receiver_id_users",
        "call_sessions",
        "users",
        ["receiver_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "fk_call_sessions_receiver_id_users",
        "call_sessions",
        type_="foreignkey",
    )

    op.drop_column(
        "call_sessions",
        "receiver_id",
    )