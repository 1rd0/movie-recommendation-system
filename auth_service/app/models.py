# auth_service/app/models.py
from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    password: str

class LoginData(BaseModel):
    email: str
    password: str

class TokenData(BaseModel):
    access_token: str
    token_type: str

