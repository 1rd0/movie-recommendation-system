from typing import List
from pydantic import BaseModel
from app.schemas.review import ReviewResponse

class MovieResponse(BaseModel):
    id: int
    title: str
    release_year: str
    reviews: List[ReviewResponse]  

    class Config:
        orm_mode = True
