from fastapi import FastAPI, HTTPException
from typing import List
import aiohttp
import numpy as np
import faiss
import requests
from datetime import datetime

app = FastAPI()

# Конфигурация FAISS и модели для извлечения векторов
FAISS_INDEX_PATH = "E:/movie-recommendation-system/recommendation_service/index.faiss"  # Путь к FAISS индексу
DIM = 1024  # Размерность векторов

# Загрузка индекса FAISS
index = faiss.read_index(FAISS_INDEX_PATH)

# URL-ы внешних сервисов
USER_SERVICE_URL = "http://localhost:8000"  # URL User Service
MOVIE_SERVICE_URL = "http://localhost:8001"  # URL Movie Service
EMBEDDING_SERVICE_URL = "http://localhost:11434/api/embeddings"  # URL для извлечения эмбеддингов

# Функция для получения векторов эмбеддингов
def get_embedding_from_ollama(prompt: str) -> np.ndarray:
    try:
        response = requests.post(
            EMBEDDING_SERVICE_URL,
            json={"model": "mxbai-embed-large", "prompt": prompt},
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        if "embedding" in data:
            return np.array(data["embedding"], dtype="float32")
        else:
            raise ValueError("Embedding not found in response")
    except Exception as e:
        print(f"Error fetching embedding: {e}")
        return None

# Функция для вычисления вектора профиля пользователя
def get_user_profile_embedding(user_history, movie_metadata, current_date=None, lambda_=0.01):
    user_embedding = np.zeros(DIM, dtype="float32")
    total_weight = 0

    if current_date is None:
        current_date = datetime.now()

    for entry in user_history:
        movie_id = entry["movie_id"]
        rating = entry["rating"]
        watched_at = datetime.fromisoformat(entry["watched_at"])
        prompt = movie_metadata[movie_id]["textual_representation"]
        embedding = get_embedding_from_ollama(prompt)

        if embedding is not None:
            time_diff = (current_date - watched_at).days
            time_weight = np.exp(-lambda_ * time_diff)
            weight = rating * time_weight
            user_embedding += embedding * weight
            total_weight += weight

    if total_weight > 0:
        user_embedding /= total_weight

    return user_embedding

@app.get("/recommendations/{user_id}/", summary="Get movie recommendations for a user")
async def get_recommendations(user_id: int) -> List[dict]:
    """
    Генерация рекомендаций на основе истории просмотров пользователя и векторного поиска.
    """
    try:
        # Шаг 1: Получаем историю просмотров пользователя
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{USER_SERVICE_URL}/users/{user_id}/history/") as response:
                if response.status != 200:
                    raise HTTPException(status_code=response.status, detail="Failed to fetch user history")
                history = await response.json()

        if not history:
            return {"message": "No history found for this user", "recommendations": []}

        # Шаг 2: Получаем метаданные фильмов из Movie Service
        movie_metadata = {}
        async with aiohttp.ClientSession() as session:
            for entry in history:
                movie_id = entry["movie_id"]
                async with session.get(f"{MOVIE_SERVICE_URL}/movies/{movie_id}/") as response:
                    if response.status == 200:
                        movie = await response.json()
                        movie_metadata[movie_id] = {
                            "textual_representation": f"""Type: {movie['type']},
Title: {movie['title']},
Director: {movie['director']},
Cast: {movie['cast']},
Released: {movie['release_year']},
Genres: {movie['genres']},
Description: {movie['description']}"""
                        }

        # Шаг 3: Вычисляем вектор профиля пользователя
        user_profile_embedding = get_user_profile_embedding(history, movie_metadata)

        if user_profile_embedding is None:
            raise HTTPException(status_code=500, detail="Failed to compute user profile embedding")

        # Шаг 4: Выполняем поиск по FAISS индексу
        user_profile_embedding = user_profile_embedding.reshape(1, -1)
        D, I = index.search(user_profile_embedding, 10)  # 10 рекомендаций
        recommended_movie_ids = I.flatten()

        # Шаг 5: Формируем рекомендации
        recommendations = []
        async with aiohttp.ClientSession() as session:
            for movie_id in recommended_movie_ids:
                async with session.get(f"{MOVIE_SERVICE_URL}/movies/{movie_id}/") as response:
                    if response.status == 200:
                        movie = await response.json()
                        recommendations.append(movie)

        return {"recommendations": recommendations}

    except Exception as e:
        print(f"Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
