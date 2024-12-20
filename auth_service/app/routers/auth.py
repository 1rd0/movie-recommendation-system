# auth_service/app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException
from datetime import timedelta
from app.models import LoginData
from app.services.dependencies import get_db_pool
from app.services.auth_service import authenticate_user, create_access_token
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

@router.post("/login/")
async def login_for_access_token(login_data: LoginData, db_pool=Depends(get_db_pool)):
    user = await authenticate_user(db_pool, login_data.email, login_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token({"sub": str(user["id"])}, access_token_expires)
    return {"access_token": token, "token_type": "bearer"}
