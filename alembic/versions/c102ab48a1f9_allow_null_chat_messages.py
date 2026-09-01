"""allow null chat messages

Revision ID: c102ab48a1f9
Revises: 44fcd613efcd
Create Date: 2026-08-31

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c102ab48a1f9"
down_revision: Union[str, Sequence[str], None] = "44fcd613efcd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Allow file-only chat messages."""

    op.alter_column(
        "chat_history",
        "message",
        existing_type=sa.Text(),
        nullable=True,
    )


def downgrade() -> None:
    """Make chat messages required again."""

    op.alter_column(
        "chat_history",
        "message",
        existing_type=sa.Text(),
        nullable=False,
    )