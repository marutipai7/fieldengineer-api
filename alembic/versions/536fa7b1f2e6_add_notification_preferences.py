"""add notification preferences

Revision ID: 536fa7b1f2e6
Revises: 58f9ef782358
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "536fa7b1f2e6"
down_revision: Union[str, Sequence[str], None] = "58f9ef782358"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "notification_preferences",

        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),

        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False,
        ),

        # ALL
        sa.Column("all_priority_jobs", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("all_new_job_requests", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("all_job_assigned", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("all_job_reminders", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("all_job_updates", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("all_chat_messages", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("all_missed_messages_reminder", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("all_payment_received", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("all_payout_updates", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("all_app_updates", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("all_maintenance_alerts", sa.Boolean(), server_default=sa.true(), nullable=False),

        # BOOKINGS
        sa.Column("booking_new_job_requests", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("booking_job_assigned", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("booking_job_reminders", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("booking_job_updates", sa.Boolean(), server_default=sa.true(), nullable=False),

        # ENGINEER
        sa.Column("engineer_priority_jobs", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("engineer_job_assigned", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("engineer_job_updates", sa.Boolean(), server_default=sa.true(), nullable=False),

        # COMMUNICATION
        sa.Column("communication_chat_messages", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column(
            "communication_missed_messages_reminder",
            sa.Boolean(),
            server_default=sa.true(),
            nullable=False,
        ),

        # Timestamps
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

        sa.PrimaryKeyConstraint("id"),

        sa.UniqueConstraint(
            "user_id",
            name="uq_notification_preferences_user_id",
        ),
    )

    # Match the model's index=True on id
    op.create_index(
        "ix_notification_preferences_id",
        "notification_preferences",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_notification_preferences_id",
        table_name="notification_preferences",
    )

    op.drop_table("notification_preferences")