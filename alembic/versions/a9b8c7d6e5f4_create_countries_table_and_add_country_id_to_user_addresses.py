"""create countries table and add country_id to user_addresses

Revision ID: a9b8c7d6e5f4
Revises: fc3efa071e75
Create Date: 2026-09-01 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a9b8c7d6e5f4'
down_revision: Union[str, Sequence[str], None] = 'fc3efa071e75'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create countries table
    op.create_table('countries',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('code', sa.String(length=2), nullable=False),
    sa.Column('phone_code', sa.String(length=10), nullable=True),
    sa.Column('region', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name'),
    sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_countries_id'), 'countries', ['id'], unique=False)
    
    # Add country_id column to user_addresses
    op.add_column('user_addresses', 
        sa.Column('country_id', sa.Integer(), nullable=True)
    )
    
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_user_addresses_country_id',
        'user_addresses', 'countries',
        ['country_id'], ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Remove foreign key
    op.drop_constraint('fk_user_addresses_country_id', 'user_addresses', type_='foreignkey')
    
    # Remove country_id column
    op.drop_column('user_addresses', 'country_id')
    
    # Drop countries table
    op.drop_index(op.f('ix_countries_id'), table_name='countries')
    op.drop_table('countries')
