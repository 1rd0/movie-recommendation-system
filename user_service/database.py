# database.py
import asyncpg
import aio_pika
from fastapi import FastAPI

DATABASE_URL = "postgresql://postgres:postgres@localhost:5433/postgres"
RABBITMQ_URL = "amqp://rmuser:rmpassword@localhost:5672/"

async def init_db_and_rabbitmq(app: FastAPI):
    try:
        print("Initializing database pool...")
        app.state.db_pool = await asyncpg.create_pool(DATABASE_URL)
        print("Database pool initialized successfully.")

        print("Connecting to RabbitMQ...")
        app.state.rabbitmq_connection = await aio_pika.connect_robust(RABBITMQ_URL)
        print("RabbitMQ connection initialized successfully.")
    except Exception as e:
        print(f"Error during initialization: {e}")
        raise e

async def close_db_and_rabbitmq(app: FastAPI):
    try:
        if hasattr(app.state, 'db_pool'):
            await app.state.db_pool.close()
            print("Database pool closed.")
        if hasattr(app.state, 'rabbitmq_connection'):
            await app.state.rabbitmq_connection.close()
            print("RabbitMQ connection closed.")
    except Exception as e:
        print(f"Error during shutdown: {e}")
