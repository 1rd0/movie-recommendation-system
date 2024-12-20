# auth_service/app/services/auth_service.py
import hashlib
from jose import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException
from app.config import SECRET_KEY, ALGORITHM

def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def authenticate_user(db_pool, email: str, password: str):
    async with db_pool.acquire() as conn:
        user = await conn.fetchrow("SELECT id, hashed_password FROM user WHERE email = $1", email)
        if not user:
            return None
        if user["hashed_password"] != hash_password(password):
            return None
        return user
