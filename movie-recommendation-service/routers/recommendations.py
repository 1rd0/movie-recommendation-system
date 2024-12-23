# app/routers/recommendations.py

from fastapi import APIRouter, HTTPException
from app.models import RecommendationsResponse
from app.services.users import get_user_history
from app.services.movies import get_movies_metadata, get_movies_by_ids
from app.services.index import compute_user_profile_embedding, search_similar
 
from app.config import DEFAULT_NUM_RECOMMENDATIONS
 
router = APIRouter()

@router.get("/recommendations/{user_id}/", response_model=RecommendationsResponse, summary="Get movie recommendations for a user")
async def get_recommendations(user_id: int):
    try:
 
        # Получаем историю пользователя
        history_data = await get_user_history(user_id)
        # Получаем метаданные фильмов из истории
        movie_metadata = await get_movies_metadata(history_data)
        # Генерация вектора профиля пользователя
        user_profile_embedding = await compute_user_profile_embedding(history_data, movie_metadata)

        if user_profile_embedding is None:
            raise HTTPException(status_code=500, detail="Failed to compute user profile embedding")

        # Поиск похожих фильмов в FAISS
        recommended_movie_ids = search_similar(user_profile_embedding, k=DEFAULT_NUM_RECOMMENDATIONS)
        # Получаем рекомендации по ID фильмов
        recommendations = await get_movies_by_ids(recommended_movie_ids)

         
       
        return RecommendationsResponse(recommendations=recommendations)

    except Exception as e:
        print(f"Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
