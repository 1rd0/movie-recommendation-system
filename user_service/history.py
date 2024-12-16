# history.py
from fastapi import APIRouter, HTTPException, Depends
from dependencies import get_db_pool, get_rabbitmq_connection
import aio_pika
import json

router = APIRouter()

@router.post("/users/{user_id}/history/")
async def add_history(user_id: int, movie_id: int, rating: int, 
                      db_pool=Depends(get_db_pool), 
                      rabbitmq_connection=Depends(get_rabbitmq_connection)):
    if not db_pool:
        raise HTTPException(
            status_code=500, 
            detail="Database pool not initialized. Ensure database is running and connection settings are correct."
        )
    if not rabbitmq_connection:
        raise HTTPException(
            status_code=500,
            detail="RabbitMQ connection not initialized."
        )
    try:
        async with db_pool.acquire() as connection:
            await connection.execute(
                "INSERT INTO user_history (user_id, movie_id, rating, watched_at) VALUES ($1, $2, $3, NOW())",
                user_id, movie_id, rating
            )

        # Отправляем событие о добавлении записи в историю
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
    except Exception as e:
        print(f"Error adding history: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/users/{user_id}/history/{movie_id}/")
async def update_rating(user_id: int, movie_id: int, rating: int,
                        db_pool=Depends(get_db_pool),
                        rabbitmq_connection=Depends(get_rabbitmq_connection)):
    if not db_pool:
        raise HTTPException(
            status_code=500, 
            detail="Database pool not initialized. Ensure database is running and connection settings are correct."
        )
    if not rabbitmq_connection:
        raise HTTPException(
            status_code=500,
            detail="RabbitMQ connection not initialized."
        )
    try:
        async with db_pool.acquire() as connection:
            result = await connection.execute(
                "UPDATE user_history SET rating = $1 WHERE user_id = $2 AND movie_id = $3",
                rating, user_id, movie_id
            )
            if result == "UPDATE 0":
                raise HTTPException(status_code=404, detail="Record not found")

        # Отправляем событие о обновлении рейтинга в истории
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
    except Exception as e:
        print(f"Error updating rating: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/users/{user_id}/history/{movie_id}/")
async def delete_history(user_id: int, movie_id: int,
                         db_pool=Depends(get_db_pool),
                         rabbitmq_connection=Depends(get_rabbitmq_connection)):
    if not db_pool:
        raise HTTPException(
            status_code=500, 
            detail="Database pool not initialized. Ensure database is running and connection settings are correct."
        )
    if not rabbitmq_connection:
        raise HTTPException(
            status_code=500,
            detail="RabbitMQ connection not initialized."
        )
    try:
        async with db_pool.acquire() as connection:
            result = await connection.execute(
                "DELETE FROM user_history WHERE user_id = $1 AND movie_id = $2",
                user_id, movie_id
            )
            if result == "DELETE 0":
                raise HTTPException(status_code=404, detail="Record not found")

        # Отправляем событие о удалении записи из истории
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
    except Exception as e:
        print(f"Error deleting history: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
@router.get("/users/{user_id}/history/")
async def get_history(user_id: int, 
                      db_pool=Depends(get_db_pool)):
    """
    Получить историю просмотров пользователя.
    """
    if not db_pool:
        raise HTTPException(
            status_code=500, 
            detail="Database pool not initialized. Ensure database is running and connection settings are correct."
        )
    try:
        async with db_pool.acquire() as connection:
            # Извлекаем историю просмотров пользователя из базы данных
            result = await connection.fetch(
                "SELECT movie_id, rating, watched_at FROM user_history WHERE user_id = $1 ORDER BY watched_at DESC",
                user_id
            )
            if not result:
                return {"status": "success", "data": [], "message": "No history found for this user"}

            # Преобразуем результат в список словарей
            history = [
                {
                    "movie_id": record["movie_id"],
                    "rating": record["rating"],
                    "watched_at": record["watched_at"].isoformat()
                }
                for record in result
            ]
            return {"status": "success", "data": history}
    except Exception as e:
        print(f"Error fetching history: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
