from pydantic import BaseModel, EmailStr
from typing import Optional

# Модель для создания пользователя
class UserCreate(BaseModel):
    email: EmailStr
    password: str

# Модель для логина пользователя
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Модель для получения профиля пользователя
class UserProfileCreate(BaseModel):
    name: str
    preferences: Optional[str] = None

# Модель ответа с данными пользователя
class UserResponse(BaseModel):
    id: int
    email: EmailStr

    class Config:
        orm_mode = True
