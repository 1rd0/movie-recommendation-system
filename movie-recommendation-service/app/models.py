
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
    recommended_movie_ids = fields.JSONField()  
    created_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return f"Recommendations for user {self.user_id}"
from tortoise import fields, models

class MovieRecommendationDetails(models.Model):
    id = fields.IntField(pk=True)
    recommendation = fields.ForeignKeyField(
        "models.RecommendationCache",
        related_name="movie_details",
        on_delete=fields.CASCADE
    )
    movie_id = fields.IntField(index=True)
    title = fields.CharField(max_length=255)
    genres = fields.JSONField()  # Список жанров
    description = fields.TextField(null=True)
    director = fields.CharField(max_length=255, null=True)
    cast = fields.JSONField()  # Список актёров
    created_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return f"Details for movie {self.movie_id} in recommendation {self.recommendation.id}"
