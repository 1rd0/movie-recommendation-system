from fastapi import FastAPI, HTTPException
from typing import List
import aiohttp
import numpy as np
import faiss
from datetime import datetime
from pydantic import BaseModel

app = FastAPI()

# Конфигурация FAISS и модели для извлечения векторов
FAISS_INDEX_PATH = "E:/movie-recommendation-system/recommendation_service/index.faiss"  # Путь к FAISS индексу
DIM = 1024  # Размерность векторов

# Загрузка индекса FAISS
try:
    index = faiss.read_index(FAISS_INDEX_PATH)
    print("FAISS index loaded successfully")
except Exception as e:
    print(f"Failed to load FAISS index from {FAISS_INDEX_PATH}: {e}")
    raise HTTPException(status_code=500, detail="Failed to load FAISS index")

# URL-ы внешних сервисов
USER_SERVICE_URL = "http://localhost:8000"  # URL User Service
MOVIE_SERVICE_URL = "http://localhost:8001"  # URL Movie Service
EMBEDDING_SERVICE_URL = "http://localhost:11434/api/embeddings"  # URL для извлечения эмбеддингов

# Функция для получения векторов эмбеддингов
import aiohttp
import numpy as np

async def get_embedding_from_ollama(prompt: str) -> np.ndarray:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                EMBEDDING_SERVICE_URL,
                json={"model": "mxbai-embed-large", "prompt": prompt},
               
            ) as response:
                response.raise_for_status()
                data = await response.json()

                # Логирование содержимого ответа
                print(f"Received response for prompt: {prompt}")
                print(f"Embedding response data: {data}")

                if "embedding" in data:
                    return np.array(data["embedding"], dtype="float32")
                else:
                    print(f"Embedding not found in response for prompt: {prompt}")
                    return None
    except Exception as e:
        print(f"Error fetching embedding for prompt: {prompt} - Error: {e}")
        return None


async def get_user_profile_embedding(user_history, movie_metadata, current_date=None, lambda_=0.01):
    user_embedding = np.zeros(DIM, dtype="float32")
    total_weight = 0

    if current_date is None:
        current_date = datetime.now()

    for entry in user_history:
        movie_id = entry["movie_id"]
        rating = entry["rating"]
        watched_at = datetime.fromisoformat(entry["watched_at"])

        if movie_id not in movie_metadata:
            continue

        movie = movie_metadata[movie_id]
        if not isinstance(movie, dict) or "textual_representation" not in movie:
            continue
        
        prompt = movie["textual_representation"]
        embedding = await get_embedding_from_ollama(prompt)

        if embedding is None:
            print(f"Skipping movie_id {movie_id} because no embedding was found.")
            continue  # Пропускаем фильм, если эмбеддинг не был найден

        print(f"Movie ID: {movie_id} | Embedding: {embedding[:10]}")  # Печать первых 10 значений эмбеддинга для отладки
        time_diff = (current_date - watched_at).days
        time_weight = np.exp(-lambda_ * time_diff)
        weight = rating * time_weight
        user_embedding += embedding * weight
        total_weight += weight

    if total_weight > 0:
        user_embedding /= total_weight
    else:
        print("No valid embeddings were found for user profile, returning zero vector.")

    print(f"User Profile Embedding: {user_embedding[:10]}")  # Печать первых 10 значений эмбеддинга профиля
    return user_embedding

def get_movie_metadata(entry, movie):
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

    # Check if textual_representation exists, otherwise use movie title
    textual_representation = movie.get('textual_representation', '').strip()
    if not textual_representation:
        print(f"Warning: No textual_representation for movie {movie.get('id')}. Using movie title as fallback.")
        textual_representation = movie.get('title', 'No description available')

    return {
        "id": movie.get('id'),
        "type": movie.get('type'),
        "title": movie.get('title'),
        "director": movie.get('director', 'N/A'),
        "cast": cast_members,
        "release_year": release_year,
        "genres": genres,
        "description": movie.get('description', 'N/A'),
        "textual_representation": textual_representation,  # Added fallback
    }


class MovieMetadata(BaseModel):
    id: int
    type: str
    title: str
    director: str
    cast: List[str]
    release_year: str
    genres: List[str]
    description: str

class RecommendationsResponse(BaseModel):
    recommendations: List[MovieMetadata]

@app.get("/recommendations/{user_id}/", response_model=RecommendationsResponse, summary="Get movie recommendations for a user")
async def get_recommendations(user_id: int):
    try:
        # Получаем историю пользователя
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{USER_SERVICE_URL}/users/{user_id}/history/") as response:
                if response.status != 200:
                    raise HTTPException(status_code=response.status, detail="Failed to fetch user history")
                history = await response.json()

        print(f"User history fetched: {history}")

        if "data" not in history or not isinstance(history["data"], list):
            raise HTTPException(status_code=500, detail="Invalid user history format")

        # Загружаем метаданные фильмов
        movie_metadata = {}
        async with aiohttp.ClientSession() as session:
            for entry in history["data"]:
                movie_id = entry.get("movie_id")
                if movie_id is None:
                    print(f"Warning: Movie ID not found in user history entry {entry}")
                    continue
                async with session.get(f"{MOVIE_SERVICE_URL}/movies/{movie_id}/") as response:
                    if response.status == 200:
                        movie = await response.json()
                        if isinstance(movie, dict):
                            movie_metadata[movie_id] = get_movie_metadata(entry, movie)
                    else:
                        print(f"Failed to fetch movie metadata for {movie_id}, status code: {response.status}")

        if not movie_metadata:
            raise HTTPException(status_code=500, detail="No valid movie metadata found")

        # Генерация вектора профиля пользователя
        user_profile_embedding = await get_user_profile_embedding(history["data"], movie_metadata)

        if user_profile_embedding is None:
            raise HTTPException(status_code=500, detail="Failed to compute user profile embedding")

        # Поиск в FAISS индексе для схожих фильмов
        user_profile_embedding = user_profile_embedding.reshape(1, -1)
        D, I = index.search(user_profile_embedding, 3)  # 3 рекомендации
        recommended_movie_ids = I.flatten()

        print(f"Recommended movie ids: {recommended_movie_ids}")

        # Получаем рекомендации по фильмам
        recommendations = []
        async with aiohttp.ClientSession() as session:
            for movie_id in recommended_movie_ids:
                async with session.get(f"{MOVIE_SERVICE_URL}/movies/{movie_id}/") as response:
                    if response.status == 200:
                        movie = await response.json()
                        movie_data = get_movie_metadata({}, movie)  # Добавляем проверку наличия эмбеддинга
                        if movie_data:
                            recommendations.append(movie_data)

        if not recommendations:
            raise HTTPException(status_code=500, detail="No valid movie recommendations available")

        # Возвращаем данные в правильном формате
        return RecommendationsResponse(recommendations=recommendations)

    except Exception as e:
        print(f"Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
