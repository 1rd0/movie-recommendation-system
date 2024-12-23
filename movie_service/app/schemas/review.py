from pydantic import BaseModel
from typing import Optional

class ReviewCreate(BaseModel):
    movie_id: int  # ID фильма, к которому относится отзыв
    user_id: int   # ID пользователя, оставившего отзыв
    rating: int    # Рейтинг (например, от 1 до 5)
    review_text: Optional[str] = None  # Текст отзыва, опционально

class ReviewUpdate(BaseModel):
    rating: Optional[int] = None  # Изменение рейтинга
    review_text: Optional[str] = None  # Изменение текста отзыва

from pydantic import BaseModel
from typing import Optional

from datetime import datetime

class ReviewResponse(BaseModel):
    id: int
    movie_id: int
    user_id: int
    rating: int
    review_text: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
