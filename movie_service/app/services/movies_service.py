# app/services/movies_service.py
from fastapi import HTTPException
from app.repositories.movies_repo import MovieRepository

 
class MovieService:
    def __init__(self, repo: MovieRepository, rabbitmq_connection):
        self.repo = repo
        self.rabbitmq_connection = rabbitmq_connection

    async def get_movie(self, movie_id: int):
        movie = await self.repo.get_movie_by_id(movie_id)
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        return {
            "id": movie.id,
            "type": movie.type,
            "title": movie.title,
            "director": movie.director,
            "cast": movie.cast_members,
            "release_year": movie.release_year,
            "genres": movie.genres,
            "description": movie.description,
            "textual_representation": movie.textual_representation
        }

    async def search_movies(self, title: str, genre: str, director: str):
        if not title and not genre and not director:
            raise HTTPException(status_code=422, detail="At least one search parameter must be provided")

        movies = await self.repo.search_movies(title, genre, director)
        if not movies:
            raise HTTPException(status_code=404, detail="No movies found matching the criteria")

        return [
            {
                "id": m.id,
                "type": m.type,
                "title": m.title,
                "director": m.director,
                "cast": m.cast_members,
                "release_year": m.release_year,
                "genres": m.genres,
                "description": m.description,
                "textual_representation": m.textual_representation
            }
            for m in movies
        ]

    async def add_movie(self, movie):
        textual_representation = movie.create_textual_representation()
        movie_id = await self.repo.create_movie(
            type_=movie.type,
            title=movie.title,
            director=movie.director,
            cast=movie.cast_members,
            release_year=movie.release_year,
            genres=movie.genres,
            description=movie.description,
            textual_representation=textual_representation
        )
         

        return {"id": movie_id, "message": "Movie added successfully"}

    async def update_movie(self, movie_id: int, movie):
        updated_textual_representation = movie.create_textual_representation()
        updated = await self.repo.update_movie(
            movie_id,
            movie.type, movie.title, movie.director, movie.cast_members,
            movie.release_year, movie.genres, movie.description,
            updated_textual_representation
        )
        if not updated:
            raise HTTPException(status_code=404, detail="Movie not found")
        # Отправить событие в RabbitMQ, если нужно
        return {"id": movie_id, "message": "Movie updated successfully"}

    async def delete_movie(self, movie_id: int):
        deleted = await self.repo.delete_movie(movie_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Movie not found")
        return {"id": movie_id, "message": "Movie deleted successfully"}
