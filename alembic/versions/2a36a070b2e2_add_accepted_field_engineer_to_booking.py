"""add accepted field engineer to booking

Revision ID: 2a36a070b2e2
Revises: e100a0a66853
Create Date: 2026-08-10 16:42:31.419084

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2a36a070b2e2'
down_revision: Union[str, Sequence[str], None] = 'e100a0a66853'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'bookings',
        sa.Column(
            'accepted_field_engineer_id',
            sa.Integer(),
            nullable=True
        )
    )

    op.create_foreign_key(
        'fk_bookings_accepted_field_engineer',
        'bookings',
        'user_profiles',
        ['accepted_field_engineer_id'],
        ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    op.drop_constraint(
        'fk_bookings_accepted_field_engineer',
        'bookings',
        type_='foreignkey'
    )

    op.drop_column(
        'bookings',
        'accepted_field_engineer_id'
    )
