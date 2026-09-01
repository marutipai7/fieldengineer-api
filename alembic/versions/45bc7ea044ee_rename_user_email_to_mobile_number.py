from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "45bc7ea044ee"
down_revision: Union[str, Sequence[str], None] = "c102ab48a1f9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Rename users.email to users.mobile_number."""

    op.alter_column(
        "users",
        "email",
        new_column_name="mobile_number",
        existing_type=sa.String(length=255),
        existing_nullable=False,
    )

    op.alter_column(
        "users",
        "mobile_number",
        existing_type=sa.String(length=255),
        type_=sa.String(length=20),
        existing_nullable=False,
    )


def downgrade() -> None:
    """Rename users.mobile_number back to users.email."""

    op.alter_column(
        "users",
        "mobile_number",
        new_column_name="email",
        existing_type=sa.String(length=20),
        existing_nullable=False,
    )

    op.alter_column(
        "users",
        "email",
        existing_type=sa.String(length=20),
        type_=sa.String(length=255),
        existing_nullable=False,
    )