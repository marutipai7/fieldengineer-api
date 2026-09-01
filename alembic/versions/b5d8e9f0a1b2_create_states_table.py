"""create states table

Revision ID: b5d8e9f0a1b2
Revises: 
Create Date: 2026-09-01 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b5d8e9f0a1b2'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create states table
    op.create_table('states',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('code', sa.String(length=10), nullable=False),
    sa.Column('country_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    sa.ForeignKeyConstraint(['country_id'], ['countries.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name', 'country_id', name='uq_state_name_country_id'),
    sa.UniqueConstraint('code', 'country_id', name='uq_state_code_country_id')
    )
    op.create_index(op.f('ix_states_id'), 'states', ['id'], unique=False)
    op.create_index(op.f('ix_states_country_id'), 'states', ['country_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop states table
    op.drop_index(op.f('ix_states_country_id'), table_name='states')
    op.drop_index(op.f('ix_states_id'), table_name='states')
    op.drop_table('states')
