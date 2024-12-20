from fastapi import APIRouter, HTTPException, Depends
from tortoise.exceptions import DoesNotExist
from app.models import User, UserHistory
from app.dependencies import get_rabbitmq_connection
import aio_pika
import json

router = APIRouter()

@router.post("/users/{user_id}/history/")
async def add_history(user_id: int, movie_id: int, rating: int, rabbitmq_connection=Depends(get_rabbitmq_connection)):
    try:
        user = await User.get(id=user_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")

    await UserHistory.create(user=user, movie_id=movie_id, rating=rating)

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
            await channel.default_exchange.publish(
                message, routing_key="history_events"
            )

    return {"status": "success", "message": "History added"}

@router.put("/users/{user_id}/history/{movie_id}/")
async def update_rating(user_id: int, movie_id: int, rating: int, rabbitmq_connection=Depends(get_rabbitmq_connection)):
    history_record = await UserHistory.filter(user_id=user_id, movie_id=movie_id).first()
    if not history_record:
        raise HTTPException(status_code=404, detail="Record not found")

    history_record.rating = rating
    await history_record.save()

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
            await channel.default_exchange.publish(
                message, routing_key="history_events"
            )

    return {"status": "success", "message": "Rating updated"}

@router.delete("/users/{user_id}/history/{movie_id}/")
async def delete_history(user_id: int, movie_id: int, rabbitmq_connection=Depends(get_rabbitmq_connection)):
    history_record = await UserHistory.filter(user_id=user_id, movie_id=movie_id).first()
    if not history_record:
        raise HTTPException(status_code=404, detail="Record not found")

    await history_record.delete()

    if rabbitmq_connection:
        async with rabbitmq_connection.channel() as channel:
            await channel.declare_queue("history_events", durable=True)
            message_body = json.dumps({
                "event": "history_deleted",
                "user_id": user_id,
                "movie_id": movie_id
            })
            message = aio_pika.Message(body=message_body.encode())
            await channel.default_exchange.publish(
                message, routing_key="history_events"
            )

    return {"status": "success", "message": "History deleted"}

@router.get("/users/{user_id}/history/")
async def get_history(user_id: int):
    # Проверка наличия пользователя (опционально)
    user_exists = await User.exists(id=user_id)
    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found")

    records = await UserHistory.filter(user_id=user_id).order_by("-watched_at")
    history = [
        {
            "movie_id": record.movie_id,
            "rating": record.rating,
            "watched_at": record.watched_at.isoformat()
        } for record in records
    ]
    return {"status": "success", "data": history if history else [], "message": "No history found for this user" if not history else ""}
