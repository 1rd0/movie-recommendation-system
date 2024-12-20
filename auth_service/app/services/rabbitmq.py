# auth_service/app/services/rabbitmq.py
import aio_pika
from fastapi import FastAPI
from app.config import RABBITMQ_URL

async def init_rabbitmq(app: FastAPI):
    app.state.rabbitmq_connection = await aio_pika.connect_robust(RABBITMQ_URL)
    print("RabbitMQ connection initialized for auth_service.")

async def close_rabbitmq(app: FastAPI):
    if hasattr(app.state, 'rabbitmq_connection'):
        await app.state.rabbitmq_connection.close()
        print("RabbitMQ connection closed for auth_service.")
