# app/repositories/movies_repo.py
from typing import Optional, List
from tortoise.exceptions import DoesNotExist
from app.models import Movie
from app.models import DirectorMovies
class MovieRepository:

    async def add_director_to_movie(self, movie_id: int, director_name: str) -> bool:
        movie = await self.get_movie_by_id(movie_id)
        if not movie:
            return False
        await DirectorMovies.create(movie=movie, director_name=director_name)
        return True

    async def get_directors_by_movie(self, movie_id: int):
        return await DirectorMovies.filter(movie_id=movie_id).all()

    async def get_movie_by_id(self, movie_id: int) -> Optional[Movie]:
        return await Movie.get_or_none(id=movie_id)

    async def search_movies(self, title: Optional[str], genre: Optional[str], director: Optional[str]) -> List[Movie]:
        
        query = Movie.all()
        if title:
            query = query.filter(title__icontains=title)
        if genre:
            query = query.filter(genres__icontains=genre)
        if director:
            query = query.filter(director__icontains=director)
        return await query

    async def create_movie(self, type_: str, title: str, director: str, cast: str,
                           release_year: str, genres: str, description: str, textual_representation: str) -> int:
        movie = await Movie.create(
            type=type_,
            title=title,
            director=director,
            cast_members=cast,
            release_year=release_year,
            genres=genres,
            description=description,
            textual_representation=textual_representation
        )
        return movie.id

    async def update_movie(self, movie_id: int, type_: Optional[str], title: Optional[str], director: Optional[str],
                           cast: Optional[str], release_year: Optional[str], genres: Optional[str],
                           description: Optional[str], textual_representation: str) -> bool:
        try:
            movie = await Movie.get(id=movie_id)
        except DoesNotExist:
            return False

        if type_ is not None:
            movie.type = type_
        if title is not None:
            movie.title = title
        if director is not None:
            movie.director = director
        if cast is not None:
            movie.cast_members = cast
        if release_year is not None:
            movie.release_year = release_year
        if genres is not None:
            movie.genres = genres
        if description is not None:
            movie.description = description
        movie.textual_representation = textual_representation

        await movie.save()
        return True

    async def delete_movie(self, movie_id: int) -> bool:
        deleted_count = await Movie.filter(id=movie_id).delete()
        return deleted_count > 0
