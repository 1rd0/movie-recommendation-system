from fastapi import APIRouter, HTTPException, Depends
from app.models import UserHistory
from app.dependencies import get_rabbitmq_connection
import aio_pika
import json
import httpx
router = APIRouter()

async def validate_user(user_id: int):
    """
    Функция для проверки существования пользователя через API сервиса авторизации.
    """
     
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://localhost:8005/users/{user_id}")
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="User not found")

@router.post("/users/{user_id}/history/")
async def add_history(user_id: int, movie_id: int, rating: int, rabbitmq_connection=Depends(get_rabbitmq_connection)):
     
    # Создание записи в истории
    await UserHistory.create(user_id=user_id, movie_id=movie_id, rating=rating)

    # Отправка события в RabbitMQ
    if rabbitmq_connection:
        async with rabbitmq_connection.channel() as channel:
            await channel.declare_queue("history_events", durable=True)
            message_body = json.dumps({
                "event": "history_added",
                "user_id": user_id,
                "movie_id": movie_id,
                "rating": rating
            })
            message = aio_pika.Message(body=message_body.encode())
            await channel.default_exchange.publish(message, routing_key="history_events")

    return {"status": "success", "message": "History added"}

@router.put("/users/{user_id}/history/{movie_id}/")
async def update_rating(user_id: int, movie_id: int, rating: int, rabbitmq_connection=Depends(get_rabbitmq_connection)):
    await validate_user(user_id)  # Проверка пользователя через сервис авторизации

    history_record = await UserHistory.filter(user_id=user_id, movie_id=movie_id).first()
    if not history_record:
        raise HTTPException(status_code=404, detail="Record not found")

    history_record.rating = rating
    await history_record.save()

    # Отправка события в RabbitMQ
    if rabbitmq_connection:
        async with rabbitmq_connection.channel() as channel:
            await channel.declare_queue("history_events", durable=True)
            message_body = json.dumps({
                "event": "history_rating_updated",
                "user_id": user_id,
                "movie_id": movie_id,
                "new_rating": rating
            })
            message = aio_pika.Message(body=message_body.encode())
            await channel.default_exchange.publish(message, routing_key="history_events")

    return {"status": "success", "message": "Rating updated"}

@router.delete("/users/{user_id}/history/{movie_id}/")
async def delete_history(user_id: int, movie_id: int, rabbitmq_connection=Depends(get_rabbitmq_connection)):
     

    history_record = await UserHistory.filter(user_id=user_id, movie_id=movie_id).first()
    if not history_record:
        raise HTTPException(status_code=404, detail="Record not found")

    await history_record.delete()

    # Отправка события в RabbitMQ
    if rabbitmq_connection:
        async with rabbitmq_connection.channel() as channel:
            await channel.declare_queue("history_events", durable=True)
            message_body = json.dumps({
                "event": "history_deleted",
                "user_id": user_id,
                "movie_id": movie_id
            })
            message = aio_pika.Message(body=message_body.encode())
            await channel.default_exchange.publish(message, routing_key="history_events")

    return {"status": "success", "message": "History deleted"}

@router.get("/users/{user_id}/history/")
async def get_history(user_id: int):
     

    records = await UserHistory.filter(user_id=user_id).order_by("-watched_at")
    history = [
        {
            "movie_id": record.movie_id,
            "rating": record.rating,
            "watched_at": record.watched_at.isoformat()
        } for record in records
    ]
    return {"status": "success", "data": history if history else [], "message": "No history found for this user" if not history else ""}
