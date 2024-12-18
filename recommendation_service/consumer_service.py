import asyncio
import aio_pika
import asyncpg
import numpy as np
from aio_pika import Message
from typing import Any

# Конфигурация RabbitMQ и PostgreSQL
POSTGRES_URL = "postgresql://postgres:postgres@localhost:5433/postgres"
RABBITMQ_URL = "amqp://rmuser:rmpassword@localhost:5672/"

 
QUEUE_NAME = "movie_added"
EMBEDDING_DIM = 1024  # Размерность эмбеддингов

# Функция для получения эмбеддинга с использованием Ollama
async def get_embedding_from_ollama(prompt: str) -> np.ndarray:
    import aiohttp
    EMBEDDING_SERVICE_URL = "http://localhost:11434/api/embeddings"

    async with aiohttp.ClientSession() as session:
        async with session.post(
            EMBEDDING_SERVICE_URL,
            json={"model": "mxbai-embed-large", "prompt": prompt},
        ) as response:
            response.raise_for_status()
            data = await response.json()

            if "embedding" in data:
                return np.array(data["embedding"], dtype="float32")
            else:
                raise ValueError("No embedding found in response")

# Функция для сохранения эмбеддинга в базу данных
async def save_embedding_to_db(connection: asyncpg.Connection, movie_id: int, embedding: np.ndarray):
    query = """
    INSERT INTO embeddings (movie_id, embedding)
    VALUES ($1, $2)
    ON CONFLICT (movie_id) DO NOTHING
    """
    await connection.execute(query, movie_id, embedding.tolist())

# Обработчик сообщений RabbitMQ
import json

async def process_message(message: aio_pika.Message, db_pool: asyncpg.Pool):
    async with message.process():
        try:
            # Декодирование тела сообщения
            body = message.body.decode()
            print(f"Received message: {body}")

            # Парсинг JSON
            data = json.loads(body)

            movie_id = data.get("id")
            textual_representation = data.get("textual_representation")

            if not movie_id or not textual_representation:
                print("Invalid message format")
                return

            # Генерация эмбеддинга
            embedding = await get_embedding_from_ollama(textual_representation)
            print(f"Generated embedding for movie_id {movie_id}: {embedding[:5]}...")

            # Сохранение эмбеддинга в базу данных
            async with db_pool.acquire() as connection:
                await save_embedding_to_db(connection, movie_id, embedding)

            print(f"Embedding saved successfully for movie_id {movie_id}")

        except json.JSONDecodeError:
            print("Failed to decode JSON from message.")
        except Exception as e:
            print(f"Error processing message: {e}")

# Главная функция для запуска консьюмера
async def main():
    # Подключение к PostgreSQL
    db_pool = await asyncpg.create_pool(POSTGRES_URL)
    print("Connected to PostgreSQL")

    # Подключение к RabbitMQ
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)

    # Объявление очереди
    queue = await channel.declare_queue(QUEUE_NAME, durable=True)
    print(f"Waiting for messages from queue: {QUEUE_NAME}")

    # Запуск консьюмера
    await queue.consume(lambda message: process_message(message, db_pool))

    # Бесконечный цикл для удержания консьюмера
    try:
        await asyncio.Future()
    finally:
        await connection.close()
        await db_pool.close()

# Точка входа
if __name__ == "__main__":
    asyncio.run(main())
