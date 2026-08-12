"""create engineer invitation table

Revision ID: b2c3d4e5f6a7
Revises: fc3efa071e75
Create Date: 2026-08-12 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, Sequence[str], None] = '483194352f9d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('engineer_invitations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('vendor_profile_id', sa.Integer(), nullable=False),
        sa.Column('referral_token', sa.String(length=255), nullable=False),
        sa.Column('referral_link', sa.Text(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone_number', sa.String(length=20), nullable=True),
        sa.Column('is_used', sa.Boolean(), nullable=True),
        sa.Column('used_by_user_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', sa.Enum('pending', 'accepted', 'expired', name='invitation_status'), nullable=True),
        sa.ForeignKeyConstraint(['used_by_user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['vendor_profile_id'], ['vendor_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('referral_token')
    )
    op.create_index(op.f('ix_engineer_invitations_referral_token'), 'engineer_invitations', ['referral_token'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_engineer_invitations_referral_token'), table_name='engineer_invitations')
    op.drop_table('engineer_invitations')
    op.execute('DROP TYPE invitation_status')