"""fix booking fields for create update and details

Revision ID: 8abb50857d60
Revises: 2a806e3d16cd
Create Date: 2026-09-03 17:41:41.641927

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8abb50857d60'
down_revision: Union[str, Sequence[str], None] = '2a806e3d16cd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # =========================================================
    # 1. BOOKINGS
    # =========================================================

    op.add_column(
        "bookings",
        sa.Column(
            "scope_of_work",
            sa.Text(),
            nullable=True
        )
    )

    op.add_column(
        "bookings",
        sa.Column(
            "special_requirements",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false()
        )
    )

    # Remove server default after existing rows are populated
    op.alter_column(
        "bookings",
        "special_requirements",
        server_default=None
    )


    # =========================================================
    # 2. BOOKING ADDRESSES
    # =========================================================

    # Add new FK columns first
    op.add_column(
        "booking_addresses",
        sa.Column(
            "country_id",
            sa.Integer(),
            nullable=True
        )
    )

    op.add_column(
        "booking_addresses",
        sa.Column(
            "state_id",
            sa.Integer(),
            nullable=True
        )
    )

    # Add foreign keys
    op.create_foreign_key(
        "fk_booking_addresses_country_id",
        "booking_addresses",
        "countries",
        ["country_id"],
        ["id"],
        ondelete="SET NULL"
    )

    op.create_foreign_key(
        "fk_booking_addresses_state_id",
        "booking_addresses",
        "states",
        ["state_id"],
        ["id"],
        ondelete="SET NULL"
    )

    # ---------------------------------------------------------
    # Migrate old country names -> country_id
    # ---------------------------------------------------------

    op.execute(
        """
        UPDATE booking_addresses ba
        SET country_id = c.id
        FROM countries c
        WHERE ba.country IS NOT NULL
          AND LOWER(TRIM(ba.country)) = LOWER(TRIM(c.name))
        """
    )

    # ---------------------------------------------------------
    # Migrate old state names -> state_id
    # using the already populated country_id
    # ---------------------------------------------------------

    op.execute(
        """
        UPDATE booking_addresses ba
        SET state_id = s.id
        FROM states s
        WHERE ba.state IS NOT NULL
          AND ba.country_id = s.country_id
          AND LOWER(TRIM(ba.state)) = LOWER(TRIM(s.name))
        """
    )

    # Now remove old string columns
    op.drop_column(
        "booking_addresses",
        "country"
    )

    op.drop_column(
        "booking_addresses",
        "state"
    )


    # =========================================================
    # 3. ACCESS INFORMATION
    # =========================================================

    # PostgreSQL integer -> boolean conversion.
    # Existing values are expected to be 0/1.

    op.alter_column(
        "access_information",
        "visitor_pass_required",
        existing_type=sa.Integer(),
        type_=sa.Boolean(),
        existing_nullable=True,
        postgresql_using="""
            CASE
                WHEN visitor_pass_required = 1 THEN TRUE
                ELSE FALSE
            END
        """,
        server_default=sa.false()
    )

    op.alter_column(
        "access_information",
        "night_shift_access",
        existing_type=sa.Integer(),
        type_=sa.Boolean(),
        existing_nullable=True,
        postgresql_using="""
            CASE
                WHEN night_shift_access = 1 THEN TRUE
                ELSE FALSE
            END
        """,
        server_default=sa.false()
    )

    op.alter_column(
        "access_information",
        "weekend_access",
        existing_type=sa.Integer(),
        type_=sa.Boolean(),
        existing_nullable=True,
        postgresql_using="""
            CASE
                WHEN weekend_access = 1 THEN TRUE
                ELSE FALSE
            END
        """,
        server_default=sa.false()
    )

    op.alter_column(
        "access_information",
        "id_verification_required",
        existing_type=sa.Integer(),
        type_=sa.Boolean(),
        existing_nullable=True,
        postgresql_using="""
            CASE
                WHEN id_verification_required = 1 THEN TRUE
                ELSE FALSE
            END
        """,
        server_default=sa.false()
    )


    # =========================================================
    # 4. BOOKING SCHEDULE
    # =========================================================

    op.add_column(
        "booking_schedules",
        sa.Column(
            "urgency_level",
            sa.String(length=50),
            nullable=True
        )
    )

    op.add_column(
        "booking_schedules",
        sa.Column(
            "single_day",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false()
        )
    )

    op.alter_column(
        "booking_schedules",
        "single_day",
        server_default=None
    )


def downgrade() -> None:

    # =========================================================
    # BOOKING SCHEDULE
    # =========================================================

    op.drop_column(
        "booking_schedules",
        "single_day"
    )

    op.drop_column(
        "booking_schedules",
        "urgency_level"
    )


    # =========================================================
    # ACCESS INFORMATION
    # =========================================================

    op.alter_column(
        "access_information",
        "visitor_pass_required",
        existing_type=sa.Boolean(),
        type_=sa.Integer(),
        existing_nullable=True,
        nullable=False,
        postgresql_using="""
            CASE
                WHEN visitor_pass_required THEN 1
                ELSE 0
            END
        """
    )

    op.alter_column(
        "access_information",
        "night_shift_access",
        existing_type=sa.Boolean(),
        type_=sa.Integer(),
        existing_nullable=True,
        nullable=False,
        postgresql_using="""
            CASE
                WHEN night_shift_access THEN 1
                ELSE 0
            END
        """
    )

    op.alter_column(
        "access_information",
        "weekend_access",
        existing_type=sa.Boolean(),
        type_=sa.Integer(),
        existing_nullable=True,
        nullable=False,
        postgresql_using="""
            CASE
                WHEN weekend_access THEN 1
                ELSE 0
            END
        """
    )

    op.alter_column(
        "access_information",
        "id_verification_required",
        existing_type=sa.Boolean(),
        type_=sa.Integer(),
        existing_nullable=True,
        nullable=False,
        postgresql_using="""
            CASE
                WHEN id_verification_required THEN 1
                ELSE 0
            END
        """
    )


    # =========================================================
    # BOOKING ADDRESSES
    # =========================================================

    op.add_column(
        "booking_addresses",
        sa.Column(
            "country",
            sa.String(length=100),
            nullable=True
        )
    )

    op.add_column(
        "booking_addresses",
        sa.Column(
            "state",
            sa.String(length=100),
            nullable=True
        )
    )

    # Restore country/state names from IDs
    op.execute(
        """
        UPDATE booking_addresses ba
        SET country = c.name
        FROM countries c
        WHERE ba.country_id = c.id
        """
    )

    op.execute(
        """
        UPDATE booking_addresses ba
        SET state = s.name
        FROM states s
        WHERE ba.state_id = s.id
        """
    )

    op.drop_constraint(
        "fk_booking_addresses_state_id",
        "booking_addresses",
        type_="foreignkey"
    )

    op.drop_constraint(
        "fk_booking_addresses_country_id",
        "booking_addresses",
        type_="foreignkey"
    )

    op.drop_column(
        "booking_addresses",
        "state_id"
    )

    op.drop_column(
        "booking_addresses",
        "country_id"
    )


    # =========================================================
    # BOOKINGS
    # =========================================================

    op.drop_column(
        "bookings",
        "special_requirements"
    )

    op.drop_column(
        "bookings",
        "scope_of_work"
    )
