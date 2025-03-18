import asyncpg
import asyncio
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/db")

async def seed():
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL
    );
    INSERT INTO items (name) VALUES ('Sample Item 1'), ('Sample Item 2')
    ON CONFLICT DO NOTHING;
    """)
    await conn.close()

asyncio.run(seed())