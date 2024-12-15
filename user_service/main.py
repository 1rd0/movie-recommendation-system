from fastapi import FastAPI, HTTPException
import asyncpg
import aio_pika
import hashlib
import datetime

app = FastAPI()

# Настройки подключения
DATABASE_URL = "postgresql://postgres:postgres@localhost:5433/postgres"
RABBITMQ_URL = "amqp://rmuser:rmpassword@localhost:5672/"

# Глобальные переменные
db_pool = None
rabbitmq_connection = None

@app.on_event("startup")
async def startup():
    global db_pool, rabbitmq_connection
    
    db_pool = await asyncpg.create_pool(DATABASE_URL)
    rabbitmq_connection = await aio_pika.connect_robust(RABBITMQ_URL)

@app.on_event("shutdown")
async def shutdown():
    global db_pool, rabbitmq_connection
    
    await db_pool.close()
    await rabbitmq_connection.close()

# Хэширование пароля
def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

# Регистрация пользователя
@app.post("/users/")
async def create_user(email: str, password: str):
    async with db_pool.acquire() as connection:
        try:
            hashed_password = hash_password(password)
            user_id = await connection.fetchval(
                "INSERT INTO users (email, hashed_password) VALUES ($1, $2) RETURNING id",
                email, hashed_password
            )
            return {"status": "success", "user_id": user_id, "message": "User registered successfully"}
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

# Создание профиля пользователя
@app.post("/users/{user_id}/profile/")
async def create_profile(user_id: int, name: str, preferences: str = None):
    async with db_pool.acquire() as connection:
        await connection.execute(
            "INSERT INTO user_profiles (user_id, name, preferences) VALUES ($1, $2, $3)",
            user_id, name, preferences
        )
    return {"status": "success", "message": "User profile created"}

# Добавление истории просмотров
@app.post("/users/{user_id}/history/")
async def add_history(user_id: int, movie_id: int, rating: int):
    if rating < 1 or rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    async with db_pool.acquire() as connection:
        await connection.execute(
            "INSERT INTO user_history (user_id, movie_id, rating, watched_at) VALUES ($1, $2, $3, $4)",
            user_id, movie_id, rating, datetime.datetime.utcnow()
        )
    return {"status": "success", "message": "History added"}

# Отправка сообщения в RabbitMQ
@app.post("/send-message/")
async def send_message(message: str):
    async with rabbitmq_connection.channel() as channel:
        queue = await channel.declare_queue("user_history_queue", durable=True)
        await channel.default_exchange.publish(
            aio_pika.Message(body=message.encode()),
            routing_key=queue.name,
        )
    return {"status": "success", "message": "Message sent to RabbitMQ"}
