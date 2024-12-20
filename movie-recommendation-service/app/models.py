# app/models.py

from typing import List
from pydantic import BaseModel

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
