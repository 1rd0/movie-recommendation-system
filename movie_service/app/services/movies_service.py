# app/services/movies_service.py
from typing import Optional
from app.models import MovieCreate, MovieUpdate
from app.services.rabbitmq import send_movie_to_rabbitmq
from app.repositories.movies_repo import MovieRepository
from fastapi import HTTPException

class MovieService:
    def __init__(self, repo: MovieRepository, rabbitmq_connection):
        self.repo = repo
        self.rabbitmq_connection = rabbitmq_connection

    async def get_movie(self, movie_id: int):
        movie = await self.repo.get_movie_by_id(movie_id)
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        return dict(movie)

    async def search_movies(self, title: Optional[str], genre: Optional[str], director: Optional[str]):
        if not title and not genre and not director:
            raise HTTPException(status_code=422, detail="At least one search parameter must be provided")

        movies = await self.repo.search_movies(title, genre, director)
        if not movies:
            raise HTTPException(status_code=404, detail="No movies found matching the criteria")

        return [dict(m) for m in movies]

    async def add_movie(self, movie: MovieCreate):
        textual_representation = movie.create_textual_representation()
        movie_id = await self.repo.create_movie(
            type_=movie.type,
            title=movie.title,
            director=movie.director,
            cast=movie.cast,
            release_year=movie.release_year,
            genres=movie.genres,
            description=movie.description,
            textual_representation=textual_representation
        )
        if movie_id:
            await send_movie_to_rabbitmq(self.rabbitmq_connection, movie_id, textual_representation)
            return {"id": movie_id, "message": "Movie added successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to add movie")

    async def update_movie(self, movie_id: int, movie: MovieUpdate):
        # Проверяем, что фильм существует
        existing = await self.repo.get_movie_by_id(movie_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Movie not found")

        updated_textual_representation = movie.create_textual_representation()

        updated = await self.repo.update_movie(
            movie_id,
            movie.type, movie.title, movie.director,
            movie.cast, movie.release_year, movie.genres,
            movie.description, updated_textual_representation
        )
        if updated:
            await send_movie_to_rabbitmq(self.rabbitmq_connection, movie_id, updated_textual_representation)
            return {"id": movie_id, "message": "Movie updated successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to update the movie")

    async def delete_movie(self, movie_id: int):
        # Проверяем, что фильм существует
        existing = await self.repo.get_movie_by_id(movie_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Movie not found")

        deleted = await self.repo.delete_movie(movie_id)
        if deleted:
            return {"id": movie_id, "message": "Movie deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete movie")
