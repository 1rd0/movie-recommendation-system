from fastapi import FastAPI, Depends, HTTPException
import logging
import asyncpg
from typing import List, Optional
from dependencies import get_db_pool, get_rabbitmq_connection
from database import init_db_and_rabbitmq, close_db_and_rabbitmq

app = FastAPI()

@app.on_event("startup")
async def startup():
    print("Initializing resources...")
    await init_db_and_rabbitmq(app)

@app.on_event("shutdown")
async def shutdown():
    print("Releasing resources...")
    await close_db_and_rabbitmq(app)

# Эндпоинт для получения метаданных фильма по его ID
@app.get("/movies/{movie_id}/", tags=["Movies"])
async def get_movie_metadata(movie_id: int, db_pool: asyncpg.Pool = Depends(get_db_pool)):
    """
    Возвращает метаданные фильма по его ID из базы данных.
    """
    async with db_pool.acquire() as connection:
        query = """
        SELECT id, type, title, director, cast_members, release_year, genres, description, textual_representation
        FROM movies
        WHERE id = $1
        """
        movie = await connection.fetchrow(query, movie_id)

        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")

        # Преобразуем запись из базы данных в JSON-формат
        return {
            "id": movie["id"],
            "type": movie["type"],
            "title": movie["title"],
            "director": movie["director"],
            "cast": movie["cast_members"],
            "release_year": movie["release_year"],
            "genres": movie["genres"],
            "description": movie["description"],
            "textual_representation": movie['textual_representation']
        }

# Настроим базовое логирование
logging.basicConfig(level=logging.INFO)

# Эндпоинт для поиска фильмов по названию, жанру или режиссеру
@app.get("/moviessearch/", tags=["Movies"])
async def search_movies(
    title: Optional[str] = None,
    genre: Optional[str] = None,
    director: Optional[str] = None,
    db_pool: asyncpg.Pool = Depends(get_db_pool)
):
    logging.info(f"Search parameters: title={title}, genre={genre}, director={director}")

    # Если нет параметров поиска, возвращаем ошибку
    if not title and not genre and not director:
        raise HTTPException(status_code=422, detail="At least one search parameter must be provided")

    try:
        query = """
        SELECT id, type, title, director, cast_members, release_year, genres, description, textual_representation
        FROM movies
        WHERE 1=1
        """
        params = []

        # Добавляем условия поиска, если переданы параметры
        if title:
            query += " AND title ILIKE $1"
            params.append(f"%{title}%")
        if genre:
            query += " AND genres ILIKE $2"
            params.append(f"%{genre}%")
        if director:
            query += " AND director ILIKE $3"
            params.append(f"%{director}%")

        async with db_pool.acquire() as connection:
            movies = await connection.fetch(query, *params)

        if not movies:
            raise HTTPException(status_code=404, detail="No movies found matching the criteria")

        return [
            {
                "id": movie["id"],
                "type": movie["type"],
                "title": movie["title"],
                "director": movie["director"],
                "cast": movie["cast_members"],
                "release_year": movie["release_year"],  # Возможно, вам стоит убрать это, если оно не нужно
                "genres": movie["genres"],
                "description": movie["description"],
                "textual_representation": movie['textual_representation']
            }
            for movie in movies
        ]

    except Exception as e:
        logging.error(f"Error during database query: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

import aio_pika
import json
import aio_pika

async def send_movie_to_rabbitmq(rabbitmq_connection, movie_id: int, textual_representation: str):
    try:
        # Формирование JSON-объекта
        message_body = json.dumps({
            "id": movie_id,
            "textual_representation": textual_representation
        })

        # Создание канала
        channel = await rabbitmq_connection.channel()
        await channel.default_exchange.publish(
            aio_pika.Message(body=message_body.encode()),  # Кодирование JSON в байты
            routing_key="movie_added"
        )
        print("Message sent to RabbitMQ.")
    except Exception as e:
        print(f"Error sending message: {e}")

def create_textual_representation(row):
    if not row['type'] or not row['title']:
        return ""  # если данных нет, возвращаем пустую строку
    return f"""Type: {row['type']},
Title: {row['title']},
Director: {row['director']},
Cast: {row['cast']},
Released: {row['release_year']},
Genres: {row['listed_in']},

Description: {row['description']}"""
from pydantic import BaseModel
class MovieCreate(BaseModel):
    type: str
    title: str
    director: str
    cast: str
    release_year: str
    genres: str
    description: str

    def create_textual_representation(self):
        return f"""Type: {self.type},
Title: {self.title},
Director: {self.director},
Cast: {self.cast},
Released: {self.release_year},
Genres: {self.genres},

Description: {self.description}"""

# Функция для добавления фильма в базу данных
@app.post("/movies/", tags=["Movies"])
async def add_movie(movie: MovieCreate, 
                    db_pool: asyncpg.Pool = Depends(get_db_pool), 
                    rabbitmq_connection = Depends(get_rabbitmq_connection)):  # Передаем rabbitmq_connection
    """
    Добавляет новый фильм в базу данных.
    """
    try:
        # Создаем текстовое представление фильма
        textual_representation = movie.create_textual_representation()

        async with db_pool.acquire() as connection:
            # Вставляем данные в таблицу movies
            query = """
                INSERT INTO movies (type, title, director, cast_members, release_year, genres, description, textual_representation)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING id
            """
            result = await connection.fetchrow(query, 
                                                movie.type, 
                                                movie.title, 
                                                movie.director, 
                                                movie.cast, 
                                                movie.release_year,
                                                movie.genres, 
                                                movie.description, 
                                                textual_representation)
            await send_movie_to_rabbitmq(rabbitmq_connection, result["id"], textual_representation)
            # Возвращаем ID добавленного фильма
            return {"id": result["id"], "message": "Movie added successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

class MovieUpdate(BaseModel):
    type: Optional[str] = None
    title: Optional[str] = None
    director: Optional[str] = None
    cast: Optional[str] = None
    release_year: Optional[str] = None
    genres: Optional[str] = None
    description: Optional[str] = None

    def create_textual_representation(self):
        return f"""Type: {self.type or ''},
Title: {self.title or ''},
Director: {self.director or ''},
Cast: {self.cast or ''},
Released: {self.release_year or ''},
Genres: {self.genres or ''},

Description: {self.description or ''}"""

# Эндпоинт для обновления фильма
@app.put("/movies/{movie_id}/", tags=["Movies"])
async def update_movie(movie_id: int, 
                       movie: MovieUpdate, 
                       db_pool: asyncpg.Pool = Depends(get_db_pool),
                       rabbitmq_connection = Depends(get_rabbitmq_connection)):
    """
    Обновляет метаданные фильма по его ID.
    """
    async with db_pool.acquire() as connection:
        # Проверяем существование фильма
        existing_movie = await connection.fetchrow("SELECT * FROM movies WHERE id = $1", movie_id)
        if not existing_movie:
            raise HTTPException(status_code=404, detail="Movie not found")

        # Обновляем поля фильма
        query = """
        UPDATE movies
        SET type = COALESCE($1, type),
            title = COALESCE($2, title),
            director = COALESCE($3, director),
            cast_members = COALESCE($4, cast_members),
            release_year = COALESCE($5, release_year),
            genres = COALESCE($6, genres),
            description = COALESCE($7, description),
            textual_representation = $8
        WHERE id = $9
        RETURNING id
        """
        updated_textual_representation = movie.create_textual_representation()
        result = await connection.fetchrow(query, 
                                           movie.type, movie.title, movie.director, movie.cast, 
                                           movie.release_year, movie.genres, movie.description, 
                                           updated_textual_representation, movie_id)
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to update the movie")

        # Отправляем обновленные данные в RabbitMQ
        await send_movie_to_rabbitmq(rabbitmq_connection, movie_id, updated_textual_representation)

        return {"id": movie_id, "message": "Movie updated successfully"}

# Эндпоинт для удаления фильма
@app.delete("/movies/{movie_id}/", tags=["Movies"])
async def delete_movie(movie_id: int, db_pool: asyncpg.Pool = Depends(get_db_pool)):
    """
    Удаляет фильм из базы данных по его ID.
    """
    async with db_pool.acquire() as connection:
        # Проверяем существование фильма
        query_check = "SELECT * FROM movies WHERE id = $1"
        movie = await connection.fetchrow(query_check, movie_id)
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")

        # Удаляем фильм
        query_delete = "DELETE FROM movies WHERE id = $1"
        await connection.execute(query_delete, movie_id)

        return {"id": movie_id, "message": "Movie deleted successfully"}