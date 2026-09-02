"""add service detail fields to services

Revision ID: f4c8b1a9d2e7
Revises: 1b088992f370
Create Date: 2026-09-02 16:30:00.000000

Adds fields required by the Customer Service Details API:
- image_url (service image)
- about_service (about this service info)
- whats_included (JSON-encoded list of included items)
- min_duration_hours (2 hr minimum)
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f4c8b1a9d2e7"
down_revision: Union[str, Sequence[str], None] = "1b088992f370"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "services",
        sa.Column("image_url", sa.String(length=500), nullable=True),
    )
    op.add_column(
        "services",
        sa.Column("about_service", sa.Text(), nullable=True),
    )
    op.add_column(
        "services",
        sa.Column("whats_included", sa.Text(), nullable=True),
    )
    op.add_column(
        "services",
        sa.Column(
            "min_duration_hours",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("2"),
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("services", "min_duration_hours")
    op.drop_column("services", "whats_included")
    op.drop_column("services", "about_service")
    op.drop_column("services", "image_url")
