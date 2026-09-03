"""create service details table

Revision ID: a82f1285505e
Revises: a1dbf2f1f456
Create Date: 2026-09-03 16:20:43.182834

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a82f1285505e"
down_revision: Union[str, Sequence[str], None] = "a1dbf2f1f456"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "service_details",

        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False
        ),

        sa.Column(
            "service_id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "image_url",
            sa.String(length=500),
            nullable=True
        ),

        sa.Column(
            "engineers_available",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "price_per_hour",
            sa.Numeric(precision=10, scale=2),
            nullable=False
        ),

        sa.Column(
            "min_duration_hours",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "service_tags",
            sa.Text(),
            nullable=True
        ),

        sa.Column(
            "about_service",
            sa.Text(),
            nullable=True
        ),

        sa.Column(
            "whats_included",
            sa.Text(),
            nullable=True
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True
        ),

        sa.ForeignKeyConstraint(
            ["service_id"],
            ["services.id"],
            ondelete="CASCADE"
        ),

        sa.PrimaryKeyConstraint("id"),

        sa.UniqueConstraint("service_id")
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_table("service_details")