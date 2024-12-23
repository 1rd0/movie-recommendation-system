# app/models.py

from typing import List
from pydantic import BaseModel
from tortoise import fields, models
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
 

class RecommendationCache(models.Model):
    id = fields.IntField(pk=True)
    user_id = fields.IntField(index=True)
    recommended_movie_ids = fields.JSONField()  # Список ID фильмов
    created_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return f"Recommendations for user {self.user_id}"
