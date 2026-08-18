"""add work preference to user profile

Revision ID: 483194352f9d
Revises: 2a36a070b2e2
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "483194352f9d"
down_revision: Union[str, Sequence[str], None] = "2a36a070b2e2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "user_profiles",
        sa.Column(
            "work_preference",
            sa.String(length=20),
            nullable=True
        )
    )


def downgrade() -> None:
    op.drop_column(
        "user_profiles",
        "work_preference"
    )