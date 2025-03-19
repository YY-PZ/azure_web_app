import asyncpg
import asyncio
import os
import logging
from urllib.parse import quote_plus

logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

sql_url = ""
if os.getenv("WEBSITE_HOSTNAME"):
    logger.info("Connecting to Azure PostgreSQL Flexible server based on AZURE_POSTGRESQL_CONNECTIONSTRING...")
    env_connection_string = os.getenv("AZURE_POSTGRESQL_CONNECTIONSTRING")
    if env_connection_string is None:
        logger.info("Missing environment variable AZURE_POSTGRESQL_CONNECTIONSTRING")
    else:
        # Parse the connection string
        details = dict(item.split('=') for item in env_connection_string.split())

        # Properly format the URL for SQLAlchemy
        sql_url = (
            f"postgresql+asyncpg://{(details['user'])}:{quote_plus(details['password'])}"
            f"@{details['host']}:{details['port']}/{details['dbname']}?sslmode={details['sslmode']}"
        )

else:
    logger.info("Connecting to local PostgreSQL server based on .env file...")    
    sql_url = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/db")
    sql_url = sql_url.replace("postgresql+asyncpg", "postgresql")

async def seed():
    conn = await asyncpg.connect(sql_url)
    await conn.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL
    );
    INSERT INTO items (id,name) VALUES (98,'Sample Item A'), (99,'Sample Item B')
    ON CONFLICT DO NOTHING;
    """)
    await conn.close()

asyncio.run(seed())