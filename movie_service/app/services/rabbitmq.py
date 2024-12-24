
import aio_pika
from fastapi import FastAPI
from app.config import RABBITMQ_URL
import json

async def init_rabbitmq(app: FastAPI):
    app.state.rabbitmq_connection = await aio_pika.connect_robust(RABBITMQ_URL)
    print("RabbitMQ connection initialized successfully.")

async def close_rabbitmq(app: FastAPI):
    if hasattr(app.state, 'rabbitmq_connection'):
        await app.state.rabbitmq_connection.close()
        print("RabbitMQ connection closed.")

async def send_movie_to_rabbitmq(rabbitmq_connection, movie_id: int, textual_representation: str):
    try:
        message_body = json.dumps({
            "id": movie_id,
            "textual_representation": textual_representation
        })

        channel = await rabbitmq_connection.channel()
        await channel.default_exchange.publish(
            aio_pika.Message(body=message_body.encode()),
            routing_key="movie_added"
        )
        print("Message sent to RabbitMQ.")
    except Exception as e:
        print(f"Error sending message: {e}")
