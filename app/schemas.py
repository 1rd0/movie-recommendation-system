from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class HistoryCreate(BaseModel):
    movie_id: int
    rating: int

class HistoryUpdate(BaseModel):
    rating: int

class HistoryRecord(BaseModel):
    movie_id: int
    rating: int
    watched_at: datetime

    class Config:
        orm_mode = True

class HistoryResponse(BaseModel):
    status: str
    data: Optional[List[HistoryRecord]] = None
    message: Optional[str] = None
