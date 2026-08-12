"""create notification tables

Revision ID: 85c41fbb1614
Revises: e100a0a66853
Create Date: 2026-08-10 18:26:58.171786

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "85c41fbb1614"
down_revision: Union[str, Sequence[str], None] = "e100a0a66853"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "notifications",

        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),

        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "title",
            sa.String(length=255),
            nullable=False,
        ),

        sa.Column(
            "message",
            sa.Text(),
            nullable=False,
        ),

        sa.Column(
            "notification_type",
            sa.String(length=50),
            nullable=False,
        ),

        sa.Column(
            "entity_type",
            sa.String(length=50),
            nullable=True,
        ),

        sa.Column(
            "entity_id",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "type",
            sa.String(length=50),
            nullable=False,
            server_default="info",
        ),

        sa.Column(
            "notification_metadata",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),

        sa.Column(
            "is_read",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),

        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),

        sa.CheckConstraint(
            "type IN ('info', 'success', 'warning', 'error', 'promotion')",
            name="ck_notification_type",
        ),
    )

    op.create_index(
        "idx_notifications_user_is_read",
        "notifications",
        ["user_id", "is_read"],
    )

    op.create_index(
        "idx_notifications_user_created_at",
        "notifications",
        ["user_id", "created_at"],
    )

    op.create_index(
        "idx_notifications_user_type",
        "notifications",
        ["user_id", "notification_type"],
    )


def downgrade() -> None:
    op.drop_index(
        "idx_notifications_user_type",
        table_name="notifications",
    )

    op.drop_index(
        "idx_notifications_user_created_at",
        table_name="notifications",
    )

    op.drop_index(
        "idx_notifications_user_is_read",
        table_name="notifications",
    )

    op.drop_table("notifications")