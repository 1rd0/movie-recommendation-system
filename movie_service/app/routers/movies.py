# app/routers/movies.py
from fastapi import APIRouter, Depends
from asyncpg import Pool
from app.services.dependencies import get_db_pool, get_rabbitmq_connection
from app.models import MovieCreate, MovieUpdate
from app.repositories.movies_repo import MovieRepository
from app.services.movies_service import MovieService

router = APIRouter(tags=["Movies"])

@router.get("/movies/{movie_id}/")
async def get_movie_metadata(movie_id: int, db_pool: Pool = Depends(get_db_pool), rabbitmq=Depends(get_rabbitmq_connection)):
    repo = MovieRepository(db_pool)
    service = MovieService(repo, rabbitmq)
    return await service.get_movie(movie_id)

@router.get("/moviessearch/")
async def search_movies(title: str = None, genre: str = None, director: str = None,
                        db_pool: Pool = Depends(get_db_pool), rabbitmq=Depends(get_rabbitmq_connection)):
    repo = MovieRepository(db_pool)
    service = MovieService(repo, rabbitmq)
    return await service.search_movies(title, genre, director)

@router.post("/movies/")
async def add_movie(movie: MovieCreate, db_pool: Pool = Depends(get_db_pool), rabbitmq=Depends(get_rabbitmq_connection)):
    repo = MovieRepository(db_pool)
    service = MovieService(repo, rabbitmq)
    return await service.add_movie(movie)

@router.put("/movies/{movie_id}/")
async def update_movie(movie_id: int, movie: MovieUpdate, db_pool: Pool = Depends(get_db_pool), rabbitmq=Depends(get_rabbitmq_connection)):
    repo = MovieRepository(db_pool)
    service = MovieService(repo, rabbitmq)
    return await service.update_movie(movie_id, movie)

@router.delete("/movies/{movie_id}/")
async def delete_movie(movie_id: int, db_pool: Pool = Depends(get_db_pool)):
    repo = MovieRepository(db_pool)
    # Если вам нужен rabbitmq для удаления, можете передать его, но в данном случае не обязательно
    service = MovieService(repo, None)
    return await service.delete_movie(movie_id)
