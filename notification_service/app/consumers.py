import aio_pika
import json
from app.schemas import RecommendationMessage
from app.emailer import send_email
from app.config import settings

async def process_recommendation_message(message: aio_pika.IncomingMessage):
  
    async with message.process():
        try:
       
            data = json.loads(message.body.decode("utf-8"))
            recommendation_data = RecommendationMessage(**data)

          
            recommendations_list = "\n".join([f"- {item['title']}" for item in recommendation_data.recommendations])
            email_body = f"Здравствуйте!\n\nМы рады предложить вам следующие фильмы:\n\n{recommendations_list}"

        
            await send_email(recommendation_data.email, "Ваши рекомендации по фильмам", email_body)
            print(f"Рекомендации отправлены на {recommendation_data.email}")
        except Exception as e:
            print(f"Ошибка обработки сообщения: {e}")

async def start_consumer():
    """
    Запуск потребителя RabbitMQ.
    """
    connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
    channel = await connection.channel()

 
    recommendation_queue = await channel.declare_queue("recommendations", durable=False)
    await recommendation_queue.consume(process_recommendation_message)
    print("Слушатель для recommendation запущен")
