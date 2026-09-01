"""add chat attachment fields

Revision ID: 44fcd613efcd
Revises: 9b6e7e8f09b2
Create Date: 2026-08-31 17:35:14.601013

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "44fcd613efcd"
down_revision: Union[str, Sequence[str], None] = "9b6e7e8f09b2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add attachment fields to chat_history."""

    op.add_column(
        "chat_history",
        sa.Column(
            "attachment_path",
            sa.String(),
            nullable=True,
        ),
    )

    op.add_column(
        "chat_history",
        sa.Column(
            "attachment_name",
            sa.String(),
            nullable=True,
        ),
    )

    op.add_column(
        "chat_history",
        sa.Column(
            "mime_type",
            sa.String(),
            nullable=True,
        ),
    )

    op.add_column(
        "chat_history",
        sa.Column(
            "attachment_size",
            sa.Integer(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Remove attachment fields from chat_history."""

    op.drop_column(
        "chat_history",
        "attachment_size",
    )

    op.drop_column(
        "chat_history",
        "mime_type",
    )

    op.drop_column(
        "chat_history",
        "attachment_name",
    )

    op.drop_column(
        "chat_history",
        "attachment_path",
    )