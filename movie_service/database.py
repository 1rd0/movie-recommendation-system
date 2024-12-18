import asyncpg
import aio_pika
from fastapi import FastAPI

DATABASE_URL = "postgresql://postgres:postgres@localhost:5433/postgres"
RABBITMQ_URL = "amqp://rmuser:rmpassword@localhost:5672/"

async def init_db_and_rabbitmq(app: FastAPI):
    try:
        print("Initializing database pool...")
        app.state.db_pool = await asyncpg.create_pool(DATABASE_URL)
        print("Database pool initialized successfully.")

        print("Connecting to RabbitMQ...")
        app.state.rabbitmq_connection = await aio_pika.connect_robust(RABBITMQ_URL)
        print("RabbitMQ connection initialized successfully.")
    except Exception as e:
        print(f"Error during initialization: {e}")
        raise e

async def close_db_and_rabbitmq(app: FastAPI):
    try:
        if hasattr(app.state, 'db_pool'):
            await app.state.db_pool.close()
            print("Database pool closed.")
        if hasattr(app.state, 'rabbitmq_connection'):
            await app.state.rabbitmq_connection.close()
            print("RabbitMQ connection closed.")
    except Exception as e:
        print(f"Error during shutdown: {e}")

# Добавим функцию для добавления фильма
async def add_movie_to_db(db_pool: asyncpg.Pool, movie_data: dict):
    async with db_pool.acquire() as connection:
        query = """
        INSERT INTO movies (type, title, director, cast_members, release_year, genres, description, textual_representation)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        RETURNING id
        """
        result = await connection.fetchrow(query, 
                                           movie_data['type'], 
                                           movie_data['title'], 
                                           movie_data['director'],
                                           movie_data['cast_members'], 
                                           movie_data['release_year'], 
                                           movie_data['genres'], 
                                           movie_data['description'], 
                                           movie_data['textual_representation'])
        return result['id']

# Отправка сообщения в RabbitMQ
async def send_movie_to_rabbitmq(rabbitmq_connection, movie_data: dict):
    channel = await rabbitmq_connection.channel()
    await channel.default_exchange.publish(
        aio_pika.Message(body=str(movie_data).encode()),
        routing_key="movie_added"
    )