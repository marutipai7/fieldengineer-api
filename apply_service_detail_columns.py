"""
One-time helper: apply the new service detail columns directly to the
database (idempotent, safe to re-run).

Why: the live DB's alembic_version cannot currently be advanced via
`alembic upgrade head` because of pre-existing duplicate notification
migrations, so the new columns were applied manually instead.

The canonical schema changes live in:
    alembic/versions/f4c8b1a9d2e7_add_service_detail_fields_to_services.py
    alembic/versions/2a806e3d16cd_add_icon_to_services.py
    alembic/versions/a82f1285505e_create_service_details_table.py

Run as: python apply_service_detail_columns.py
"""

from app.core.database import engine
from sqlalchemy import text

STATEMENTS = [
    "ALTER TABLE services ADD COLUMN IF NOT EXISTS image_url VARCHAR(500)",
    "ALTER TABLE services ADD COLUMN IF NOT EXISTS about_service TEXT",
    "ALTER TABLE services ADD COLUMN IF NOT EXISTS whats_included TEXT",
    (
        "ALTER TABLE services ADD COLUMN IF NOT EXISTS min_duration_hours "
        "INTEGER NOT NULL DEFAULT 2"
    ),
    "ALTER TABLE services ADD COLUMN IF NOT EXISTS icon VARCHAR(100)",
    """
    CREATE TABLE IF NOT EXISTS service_details (
        id SERIAL PRIMARY KEY,
        service_id INTEGER NOT NULL UNIQUE REFERENCES services (id) ON DELETE CASCADE,
        image_url VARCHAR(500),
        engineers_available INTEGER NOT NULL,
        price_per_hour NUMERIC(10, 2) NOT NULL,
        min_duration_hours INTEGER NOT NULL,
        service_tags TEXT,
        about_service TEXT,
        whats_included TEXT,
        created_at TIMESTAMPTZ DEFAULT now(),
        updated_at TIMESTAMPTZ DEFAULT now()
    )
    """,
]

with engine.connect() as c:
    for stmt in STATEMENTS:
        c.execute(text(stmt))
        print("OK:", stmt)
    c.commit()

    cols = [
        r[0]
        for r in c.execute(text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name='services'"
        )).fetchall()
    ]
    print("services cols:", cols)