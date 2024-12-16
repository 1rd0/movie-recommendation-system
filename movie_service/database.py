import asyncpg
import aio_pika
from fastapi import FastAPI

DATABASE_URL = "postgresql://postgres:postgres@localhost:5433/postgres"
 
async def init_db_and_rabbitmq(app: FastAPI):
    try:
        print("Initializing database pool...")
        app.state.db_pool = await asyncpg.create_pool(DATABASE_URL)
        print("Database pool initialized successfully.")

        
    except Exception as e:
        print(f"Error during initialization: {e}")
        raise e

async def close_db_and_rabbitmq(app: FastAPI):
    try:
        if hasattr(app.state, 'db_pool'):
            await app.state.db_pool.close()
            print("Database pool closed.")
        
    except Exception as e:
        print(f"Error during shutdown: {e}")
