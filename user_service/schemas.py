from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserProfileCreate(BaseModel):
    name: str
    preferences: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    email: EmailStr

    class Config:
        orm_mode = True
