import pika
import json
from app.config import RABBITMQ_URL

def publish_recommendations_to_queue(user_email: str, recommendations: list):
    
    try:
        connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
        channel = connection.channel()
        channel.queue_declare(queue='recommendations')

        message = {
            "email": user_email,
            "recommendations": [
                {"title": movie["title"]} for movie in recommendations
            ]
        }
        channel.basic_publish(
            exchange='',
            routing_key='recommendations',
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)  # Устойчивость сообщений
        )
        connection.close()
        print("Message sent to RabbitMQ.")
    except Exception as e:
        print(f"Failed to send message to RabbitMQ: {e}")
