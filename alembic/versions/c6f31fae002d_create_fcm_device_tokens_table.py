"""create fcm device tokens table

Revision ID: c6f31fae002d
Revises: 7b5143774f98
Create Date: 2026-08-11 18:36:25.965109
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c6f31fae002d"
down_revision: Union[str, Sequence[str], None] = "7b5143774f98"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "fcm_device_tokens",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("token", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
    )

    op.create_index(
        "idx_fcm_device_tokens_user_id",
        "fcm_device_tokens",
        ["user_id"],
    )

    op.create_index(
        "idx_fcm_device_tokens_token",
        "fcm_device_tokens",
        ["token"],
        unique=True,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        "idx_fcm_device_tokens_token",
        table_name="fcm_device_tokens",
    )

    op.drop_index(
        "idx_fcm_device_tokens_user_id",
        table_name="fcm_device_tokens",
    )

    op.drop_table("fcm_device_tokens")