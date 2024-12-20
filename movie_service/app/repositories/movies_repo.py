# app/repositories/movies_repo.py
import asyncpg
from typing import Optional, List

class MovieRepository:
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool

    async def get_movie_by_id(self, movie_id: int) -> Optional[dict]:
        query = """
        SELECT id, type, title, director, cast_members, release_year, genres, description, textual_representation
        FROM movies
        WHERE id = $1
        """
        async with self.db_pool.acquire() as connection:
            return await connection.fetchrow(query, movie_id)

    async def search_movies(self, title: Optional[str], genre: Optional[str], director: Optional[str]) -> List[asyncpg.Record]:
        # Здесь формируем динамический запрос
        query = "SELECT id, type, title, director, cast_members, release_year, genres, description, textual_representation FROM movies WHERE 1=1"
        params = []
        if title:
            query += " AND title ILIKE $" + str(len(params)+1)
            params.append(f"%{title}%")
        if genre:
            query += " AND genres ILIKE $" + str(len(params)+1)
            params.append(f"%{genre}%")
        if director:
            query += " AND director ILIKE $" + str(len(params)+1)
            params.append(f"%{director}%")

        async with self.db_pool.acquire() as connection:
            return await connection.fetch(query, *params)

    async def create_movie(self, type_: str, title: str, director: str, cast: str, release_year: str, genres: str, description: str, textual_representation: str) -> int:
        query = """
            INSERT INTO movies (type, title, director, cast_members, release_year, genres, description, textual_representation)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id
        """
        async with self.db_pool.acquire() as connection:
            result = await connection.fetchrow(query, type_, title, director, cast, release_year, genres, description, textual_representation)
            return result["id"] if result else None

    async def update_movie(self, movie_id: int, type_: Optional[str], title: Optional[str], director: Optional[str],
                           cast: Optional[str], release_year: Optional[str], genres: Optional[str],
                           description: Optional[str], textual_representation: str) -> bool:
        query = """
        UPDATE movies
        SET 
            type = COALESCE($1, type),
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
        async with self.db_pool.acquire() as connection:
            result = await connection.fetchrow(query, type_, title, director, cast, release_year, genres, description, textual_representation, movie_id)
            return result is not None

    async def delete_movie(self, movie_id: int) -> bool:
        query = "DELETE FROM movies WHERE id = $1 RETURNING id"
        async with self.db_pool.acquire() as connection:
            result = await connection.fetchrow(query, movie_id)
            return result is not None
