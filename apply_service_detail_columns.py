"""
One-time helper: apply the new service detail columns directly to the
database (idempotent, safe to re-run).

Why: the live DB's alembic_version cannot currently be advanced via
`alembic upgrade head` because of pre-existing duplicate notification
migrations, so the new columns were applied manually instead.

The canonical schema change lives in:
    alembic/versions/f4c8b1a9d2e7_add_service_detail_fields_to_services.py

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