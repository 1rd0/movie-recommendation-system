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
from pydantic import BaseModel
from typing import Optional

class ReviewCreate(BaseModel):
    movie_id: int  
    user_id: int   
    rating: int    
    review_text: Optional[str] = None 

class ReviewUpdate(BaseModel):
    rating: Optional[int] = None 
    review_text: Optional[str] = None 

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
 