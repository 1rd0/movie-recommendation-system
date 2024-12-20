# auth_service/app/services/database.py
import asyncpg
from fastapi import FastAPI
from app.config import DATABASE_URL

async def init_db(app: FastAPI):
    app.state.db_pool = await asyncpg.create_pool(DATABASE_URL)
    print("Auth DB pool initialized.")

async def close_db(app: FastAPI):
    if hasattr(app.state, 'db_pool'):
        await app.state.db_pool.close()
        print("Auth DB pool closed.")
