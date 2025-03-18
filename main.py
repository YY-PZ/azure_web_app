from fastapi import FastAPI, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, select
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost/db")
engine = create_async_engine(DATABASE_URL, echo=True)
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
