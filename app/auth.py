from fastapi import APIRouter, HTTPException
from jose import jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
import hashlib
from tortoise.exceptions import DoesNotExist

from app.models import User

router = APIRouter()

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

class LoginData(BaseModel):
    email: str
    password: str

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/login/")
async def login_for_access_token(login_data: LoginData):
    try:
        user = await User.get(email=login_data.email)
    except DoesNotExist:
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    hashed_password = hash_password(login_data.password)
    if user.hashed_password != hashed_password:
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
