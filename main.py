from fastapi import FastAPI, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, select
import logging
from urllib.parse import quote_plus
import os

logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

# DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost/db")
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
            f"postgresql+asyncpg://{    (details['user'])}:{quote_plus(details['password'])}"
            f"@{details['host']}:{details['port']}/{details['dbname']}?sslmode={details['sslmode']}"
        )

else:
    logger.info("Connecting to local PostgreSQL server based on .env file...")    
    sql_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost/db")
engine = create_async_engine(sql_url, echo=True)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

app = FastAPI()

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()  # Закриваємо сесію асинхронно


@app.get("/", response_class=HTMLResponse)
async def read_root(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item))
    items = result.scalars().all()
    items_html = "".join(f"<li>{item.name}</li>" for item in items)
    return f"""
    <html>
        <head>
            <title>My APP</title>
        </head>
        <body>
            <h1>Test Azure WEB App!</h1>
            <form action="/items/" method="post">
                <input type="text" name="name" placeholder="Enter item name" required>
                <button type="submit">Add Item</button>
            </form>
            <h2>Items:</h2>
            <ul>{items_html}</ul>
        </body>
    </html>
    """

@app.post("/items/")
async def create_item(name: str = Form(...), db: AsyncSession = Depends(get_db)):
    new_item = Item(name=name)
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)
    return HTMLResponse(content="""
    <script>
        window.location.href = "/";
    </script>
    """)
