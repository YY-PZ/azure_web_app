from fastapi import FastAPI, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse
# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy import Column, Integer, String, select
import logging
from urllib.parse import quote_plus
import os

# from sqlalchemy.engine.url import make_url

logger = logging.getLogger("app")
logger.setLevel(logging.INFO)



app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def read_root():
    logger.info("conect to root...")  
    
    return f"""
    <html>
        <head>
            <title>My APP</title>
        </head>
        <body>
            <h1>Test Azure WEB App!!!</h1>
            <form action="/items/" method="post">
                <input type="text" name="name" placeholder="Enter item name" required>
                <button type="submit">Add Item</button>
            </form>
            <h2>Items:</h2>
            <ul></ul>
        </body>
    </html>
    """
