"""add additional task proposals

Revision ID: 816e36a60a15
Revises: c36421c727ac
Create Date: 2026-09-04 17:51:42.237435

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '816e36a60a15'
down_revision: Union[str, Sequence[str], None] = 'c36421c727ac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "additional_tasks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("booking_id", sa.Integer(), nullable=False),
        sa.Column("task_type", sa.String(length=100), nullable=False),
        sa.Column("task_description", sa.Text(), nullable=False),
        sa.Column("priority_level", sa.String(length=50), nullable=False),
        sa.Column(
            "estimated_budget",
            sa.Numeric(precision=10, scale=2),
            nullable=True,
        ),
        sa.Column(
            "estimated_duration_hours",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "estimated_duration_minutes",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["booking_id"],
            ["bookings.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "additional_task_documents",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("additional_task_id", sa.Integer(), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_url", sa.Text(), nullable=False),
        sa.Column("file_size", sa.String(length=50), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["additional_task_id"],
            ["additional_tasks.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "additional_task_proposals",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("additional_task_id", sa.Integer(), nullable=False),
        sa.Column("field_engineer_id", sa.Integer(), nullable=True),
        sa.Column(
            "proposed_cost",
            sa.Numeric(precision=10, scale=2),
            nullable=False,
        ),
        sa.Column(
            "expected_duration_hours",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "expected_duration_minutes",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "included_work",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "engineer_message",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["additional_task_id"],
            ["additional_tasks.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["field_engineer_id"],
            ["user_profiles.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_table("additional_task_proposals")
    op.drop_table("additional_task_documents")
    op.drop_table("additional_tasks")