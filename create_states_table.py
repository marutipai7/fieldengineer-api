#!/usr/bin/env python
"""Script to create the states table if it doesn't exist."""

from app.core.database import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
        # Check if states table exists
        result = conn.execute(text(
            "SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'states')"
        ))
        exists = result.scalar()
        print(f'States table exists: {exists}')
        
        if not exists:
            # Create the states table
            conn.execute(text('''
                CREATE TABLE states (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    code VARCHAR(10) NOT NULL,
                    country_id INTEGER NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    FOREIGN KEY (country_id) REFERENCES countries(id) ON DELETE CASCADE,
                    UNIQUE(name, country_id),
                    UNIQUE(code, country_id)
                )
            '''))
            conn.execute(text('CREATE INDEX ix_states_id ON states(id)'))
            conn.execute(text('CREATE INDEX ix_states_country_id ON states(country_id)'))
            conn.commit()
            print('States table created successfully')
        else:
            print('States table already exists')
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
