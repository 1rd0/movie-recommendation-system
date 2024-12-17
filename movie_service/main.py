from fastapi import FastAPI, Depends, HTTPException
from dependencies import get_db_pool
from database import init_db_and_rabbitmq,close_db_and_rabbitmq
import asyncpg

app = FastAPI()
@app.on_event("startup")
async def startup():
    print("Initializing resources...")
    await init_db_and_rabbitmq(app)

@app.on_event("shutdown")
async def shutdown():
    print("Releasing resources...")
    await close_db_and_rabbitmq(app)

@app.get("/movies/{movie_id}/", tags=["Movies"])
async def get_movie_metadata(movie_id: int, db_pool: asyncpg.Pool = Depends(get_db_pool)):
    """
    Возвращает метаданные фильма по его ID из базы данных.
    """
    async with db_pool.acquire() as connection:
        query = """
        SELECT id, type, title, director, cast_members, release_year, genres, description,textual_representation
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
            "textual_representation":movie['textual_representation']

        }
