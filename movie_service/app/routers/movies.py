# app/routers/movies.py
from fastapi import APIRouter, Depends
from app.models import MovieCreate, MovieUpdate  # Предполагается, что у вас есть такие модели DTO в models.py
from app.services.dependencies import get_rabbitmq_connection
from app.repositories.movies_repo import MovieRepository
from app.services.movies_service import MovieService

router = APIRouter(tags=["Movies"])

def get_repo():
    # Tortoise ORM не требует явного пула соединений, репозиторий может быть создан напрямую
    return MovieRepository()

@router.get("/movies/{movie_id}/")
async def get_movie_metadata(movie_id: int, repo=Depends(get_repo), rabbitmq=Depends(get_rabbitmq_connection)):
    service = MovieService(repo, rabbitmq)
    return await service.get_movie(movie_id)

@router.get("/moviessearch/")
async def search_movies(title: str = None, genre: str = None, director: str = None,
                        repo=Depends(get_repo), rabbitmq=Depends(get_rabbitmq_connection)):
    service = MovieService(repo, rabbitmq)
    return await service.search_movies(title, genre, director)

@router.post("/movies/")
async def add_movie(movie: MovieCreate, repo=Depends(get_repo), rabbitmq=Depends(get_rabbitmq_connection)):
    service = MovieService(repo, rabbitmq)
    return await service.add_movie(movie)

@router.put("/movies/{movie_id}/")
async def update_movie(movie_id: int, movie: MovieUpdate, repo=Depends(get_repo), rabbitmq=Depends(get_rabbitmq_connection)):
    service = MovieService(repo, rabbitmq)
    return await service.update_movie(movie_id, movie)

@router.delete("/movies/{movie_id}/")
async def delete_movie(movie_id: int, repo=Depends(get_repo)):
    service = MovieService(repo, None)
    return await service.delete_movie(movie_id)
