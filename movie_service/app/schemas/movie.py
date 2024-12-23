from typing import List
from pydantic import BaseModel
from app.schemas.review import ReviewResponse

class MovieResponse(BaseModel):
    id: int
    title: str
    release_year: str
    reviews: List[ReviewResponse]  # Отзывы, связанные с фильмом

    class Config:
        orm_mode = True
