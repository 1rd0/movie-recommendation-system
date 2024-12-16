from fastapi import APIRouter, HTTPException, Depends
from dependencies import get_db_pool
from jose import jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
import hashlib

router = APIRouter()

# Конфигурация для JWT
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Функция хеширования пароля (SHA-256)
def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

# Модель данных для входа пользователя
class LoginData(BaseModel):
    email: str
    password: str

# Функция генерации JWT токена
def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# POST /login - проверка пользователя и генерация токена
@router.post("/login/")
async def login_for_access_token(login_data: LoginData, db_pool=Depends(get_db_pool)):
    if not db_pool:
        raise HTTPException(status_code=500, detail="Database pool not initialized")
    
    try:
        async with db_pool.acquire() as connection:
            # Получаем пользователя из БД
            user = await connection.fetchrow(
                "SELECT id, hashed_password FROM users WHERE email = $1",
                login_data.email
            )
            if not user:
                raise HTTPException(status_code=401, detail="Incorrect email or password")

            # Проверка хешированного пароля
            hashed_password = hash_password(login_data.password)
            if user["hashed_password"] != hashed_password:
                raise HTTPException(status_code=401, detail="Incorrect email or password")
            
            # Генерация токена
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": str(user["id"])}, expires_delta=access_token_expires
            )
            return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        print(f"Error during login: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
