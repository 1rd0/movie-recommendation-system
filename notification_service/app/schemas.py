from pydantic import BaseModel, EmailStr
from typing import List

class RecommendationMessage(BaseModel):
    email: EmailStr
    recommendations: List[dict]  
