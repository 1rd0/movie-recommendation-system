import aio_pika
from fastapi import FastAPI

RABBITMQ_URL = "amqp://rmuser:rmpassword@localhost:5672/"

async def init_rabbitmq(app: FastAPI):
    app.state.rabbitmq_connection = await aio_pika.connect_robust(RABBITMQ_URL)

async def close_rabbitmq(app: FastAPI):
    if hasattr(app.state, 'rabbitmq_connection'):
        await app.state.rabbitmq_connection.close()
