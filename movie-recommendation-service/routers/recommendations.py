# app/routers/recommendations.py

from fastapi import APIRouter, HTTPException
from app.models import RecommendationsResponse
from app.services.users import get_user_history
from app.services.movies import get_movies_metadata, get_movies_by_ids,save_recommendation_to_db,save_recommendation_with_details
from app.services.index import compute_user_profile_embedding, search_similar
 
from app.config import DEFAULT_NUM_RECOMMENDATIONS
 
router = APIRouter()
from app.services.queue import publish_recommendations_to_queue
from app.services.users import get_user_email  

@router.get("/recommendations/{user_id}/", response_model=RecommendationsResponse, summary="Get movie recommendations for a user")
async def get_recommendations(user_id: int):
    try:
        
        history_data = await get_user_history(user_id)
        
       
        user_email = await get_user_email(user_id)  
        
        
        movie_metadata = await get_movies_metadata(history_data)
        
        
        user_profile_embedding = await compute_user_profile_embedding(history_data, movie_metadata)

        if user_profile_embedding is None:
            raise HTTPException(status_code=500, detail="Failed to compute user profile embedding")

        
        recommended_movie_ids = search_similar(user_profile_embedding, k=DEFAULT_NUM_RECOMMENDATIONS)
        
        
        recommendations = await get_movies_by_ids(recommended_movie_ids)
        await save_recommendation_to_db(user_id, recommended_movie_ids)
        await save_recommendation_with_details(user_id, recommendations)
       
        publish_recommendations_to_queue(user_email, recommendations)

        return RecommendationsResponse(recommendations=recommendations)

    except Exception as e:
        print(f"Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

from app.models import RecommendationCache, MovieRecommendationDetails

@router.get("/saved-recommendations/{user_id}/", summary="Get saved recommendations for a user")
async def get_saved_recommendations(user_id: int):
    try:
        recommendation_cache = await RecommendationCache.get(user_id=user_id)
        movie_details = await MovieRecommendationDetails.filter(recommendation=recommendation_cache).all()

        return {
            "user_id": user_id,
            "recommended_movies": [
                {
                    "movie_id": detail.movie_id,
                    "title": detail.title,
                    "genres": detail.genres,
                    "description": detail.description,
                    "director": detail.director,
                    "cast": detail.cast,
                }
                for detail in movie_details
            ]
        }
    except RecommendationCache.DoesNotExist:
        raise HTTPException(status_code=404, detail="Recommendations not found")
    except Exception as e:
        print(f"Error retrieving saved recommendations for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
