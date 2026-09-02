"""update customer profile fields

Revision ID: 1b088992f370
Revises: 503640006081
Create Date: 2026-09-02 13:48:47.567986

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1b088992f370"
down_revision: Union[str, Sequence[str], None] = "503640006081"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # ---------------------------------------------------------
    # Customer Bank Details
    # ---------------------------------------------------------
    op.create_table(
        "customer_bank_details",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_profile_id", sa.Integer(), nullable=False),
        sa.Column("account_holder_name", sa.String(length=255), nullable=True),
        sa.Column("bank_name", sa.String(length=255), nullable=True),
        sa.Column("account_number", sa.String(length=100), nullable=True),
        sa.Column("ifsc_code", sa.String(length=50), nullable=True),
        sa.Column("local_code", sa.String(length=50), nullable=True),
        sa.Column("bank_address", sa.Text(), nullable=True),
        sa.Column(
            "email_invoice_for_every_payout",
            sa.Boolean(),
            nullable=True,
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
            ["user_profile_id"],
            ["user_profiles.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_profile_id"),
    )

    # ---------------------------------------------------------
    # Customer Business
    # ---------------------------------------------------------
    op.add_column(
        "customer_businesses",
        sa.Column(
            "company_registration_number",
            sa.String(length=100),
            nullable=True,
        ),
    )

    op.add_column(
        "customer_businesses",
        sa.Column(
            "pan_number",
            sa.String(length=100),
            nullable=True,
        ),
    )

    op.add_column(
        "customer_businesses",
        sa.Column(
            "billing_email",
            sa.String(length=255),
            nullable=True,
        ),
    )

    # ---------------------------------------------------------
    # Customer Documents
    # ---------------------------------------------------------
    op.add_column(
        "customer_documents",
        sa.Column(
            "identity_proof",
            sa.Text(),
            nullable=True,
        ),
    )

    op.add_column(
        "customer_documents",
        sa.Column(
            "address_proof",
            sa.Text(),
            nullable=True,
        ),
    )

    # ---------------------------------------------------------
    # Customer Identity
    # ---------------------------------------------------------
    op.add_column(
        "customer_identities",
        sa.Column(
            "identity_full_name",
            sa.String(length=255),
            nullable=True,
        ),
    )

    op.add_column(
        "customer_identities",
        sa.Column(
            "date_of_birth",
            sa.Date(),
            nullable=True,
        ),
    )

    # ---------------------------------------------------------
    # User Profile
    # ---------------------------------------------------------
    op.add_column(
        "user_profiles",
        sa.Column(
            "customer_type",
            sa.String(length=30),
            nullable=True,
        ),
    )

    # ---------------------------------------------------------
    # Users
    # ---------------------------------------------------------
    op.add_column(
        "users",
        sa.Column(
            "email",
            sa.String(length=255),
            nullable=True,
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "last_login_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    # Email should be unique when provided.
    op.create_unique_constraint(
        "uq_users_email",
        "users",
        ["email"],
    )


def downgrade() -> None:
    """Downgrade schema."""

    # ---------------------------------------------------------
    # Users
    # ---------------------------------------------------------
    op.drop_constraint(
        "uq_users_email",
        "users",
        type_="unique",
    )

    op.drop_column(
        "users",
        "last_login_at",
    )

    op.drop_column(
        "users",
        "email",
    )

    # ---------------------------------------------------------
    # User Profile
    # ---------------------------------------------------------
    op.drop_column(
        "user_profiles",
        "customer_type",
    )

    # ---------------------------------------------------------
    # Customer Identity
    # ---------------------------------------------------------
    op.drop_column(
        "customer_identities",
        "date_of_birth",
    )

    op.drop_column(
        "customer_identities",
        "identity_full_name",
    )

    # ---------------------------------------------------------
    # Customer Documents
    # ---------------------------------------------------------
    op.drop_column(
        "customer_documents",
        "address_proof",
    )

    op.drop_column(
        "customer_documents",
        "identity_proof",
    )

    # ---------------------------------------------------------
    # Customer Business
    # ---------------------------------------------------------
    op.drop_column(
        "customer_businesses",
        "billing_email",
    )

    op.drop_column(
        "customer_businesses",
        "pan_number",
    )

    op.drop_column(
        "customer_businesses",
        "company_registration_number",
    )

    # ---------------------------------------------------------
    # Customer Bank Details
    # ---------------------------------------------------------
    op.drop_table(
        "customer_bank_details",
    )