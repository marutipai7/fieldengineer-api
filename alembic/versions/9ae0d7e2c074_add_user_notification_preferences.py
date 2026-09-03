"""add user notification preferences

Revision ID: 9ae0d7e2c074
Revises: a1dbf2f1f456
Create Date: 2026-09-03 17:06:35.284888

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9ae0d7e2c074"
down_revision: Union[str, Sequence[str], None] = "a1dbf2f1f456"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_notification_preferences",

        sa.Column("id", sa.Integer(), primary_key=True, index=True),

        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),

        # Main notification switch
        sa.Column("enable_notification", sa.Boolean(), nullable=False, server_default=sa.true()),

        # Notification channels
        sa.Column("push_notification", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("sms_notification", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("email_notification", sa.Boolean(), nullable=False, server_default=sa.true()),

        # Push
        sa.Column("push_priority_jobs", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("push_new_job_requests", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("push_job_assigned", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("push_job_reminders", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("push_job_updates", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("push_chat_messages", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("push_missed_messages_reminder", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("push_payment_received", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("push_payout_updates", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("push_app_updates", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("push_maintenance_alerts", sa.Boolean(), nullable=False, server_default=sa.true()),

        # SMS
        sa.Column("sms_priority_jobs", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("sms_new_job_requests", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("sms_job_assigned", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("sms_job_reminders", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("sms_job_updates", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("sms_chat_messages", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("sms_missed_messages_reminder", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("sms_payment_received", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("sms_payout_updates", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("sms_app_updates", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("sms_maintenance_alerts", sa.Boolean(), nullable=False, server_default=sa.true()),

        # Email
        sa.Column("email_priority_jobs", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("email_new_job_requests", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("email_job_assigned", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("email_job_reminders", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("email_job_updates", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("email_chat_messages", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("email_missed_messages_reminder", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("email_payment_received", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("email_payout_updates", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("email_app_updates", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("email_maintenance_alerts", sa.Boolean(), nullable=False, server_default=sa.true()),
    )


def downgrade() -> None:
    op.drop_table("user_notification_preferences")