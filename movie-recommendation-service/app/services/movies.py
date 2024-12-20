# app/services/movies.py
import aiohttp
from app.config import MOVIE_SERVICE_URL
from fastapi import HTTPException

def prepare_movie_metadata(movie: dict):
    # Приведение данных из внешнего сервиса к структуре для вычисления эмбеддингов
    cast_members = movie.get('cast', '').strip()
    if cast_members == '':
        cast_members = []
    elif isinstance(cast_members, str):
        cast_members = cast_members.split(',')

    genres = movie.get('genres', '').strip()
    if genres == '':
        genres = []
    else:
        genres = genres.split(',')

    release_year = str(movie.get('release_year', 'N/A'))

    textual_representation = movie.get('textual_representation', '').strip()
    if not textual_representation:
        print(f"Warning: No textual_representation for movie {movie.get('id')}. Skipping embedding.")
        return None

    return {
        "id": movie.get('id'),
        "type": movie.get('type'),
        "title": movie.get('title'),
        "director": movie.get('director', 'N/A'),
        "cast": cast_members,
        "release_year": release_year,
        "genres": genres,
        "description": movie.get('description', 'N/A'),
        "textual_representation": textual_representation,
    }

async def get_movies_metadata(history_entries):
    movie_metadata = {}
    async with aiohttp.ClientSession() as session:
        for entry in history_entries:
            movie_id = entry.get("movie_id")
            if movie_id is None:
                print(f"Warning: Movie ID not found in user history entry {entry}")
                continue
            async with session.get(f"{MOVIE_SERVICE_URL}/movies/{movie_id}/") as response:
                if response.status == 200:
                    movie = await response.json()
                    if isinstance(movie, dict):
                        meta = prepare_movie_metadata(movie)
                        if meta:
                            movie_metadata[movie_id] = meta
                else:
                    print(f"Failed to fetch movie metadata for {movie_id}, status code: {response.status}")

    if not movie_metadata:
        raise HTTPException(status_code=500, detail="No valid movie metadata found")
    return movie_metadata

async def get_movies_by_ids(movie_ids):
    results = []
    async with aiohttp.ClientSession() as session:
        for movie_id in movie_ids:
            async with session.get(f"{MOVIE_SERVICE_URL}/movies/{movie_id}/") as response:
                if response.status == 200:
                    movie = await response.json()
                    meta = prepare_movie_metadata(movie)
                    if meta:
                        results.append(meta)
    return results
