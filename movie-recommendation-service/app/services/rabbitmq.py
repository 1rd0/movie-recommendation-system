import aio_pika
import json
from app.config import RABBITMQ_URL

async def send_to_queue(queue_name: str, message: dict):
    try:
        connection = await aio_pika.connect_robust(RABBITMQ_URL)
        async with connection:
            channel = await connection.channel()
            queue = await channel.declare_queue(queue_name, durable=True)
            await channel.default_exchange.publish(
                aio_pika.Message(body=json.dumps(message).encode()),
                routing_key=queue_name,
            )
    except Exception as e:
        print(f"Error sending message to RabbitMQ: {e}")
