from fastapi import APIRouter, HTTPException
from app.models import User
import hashlib

router = APIRouter()

def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

@router.post("/")
async def create_user(email: str, password: str):
    hashed_password = hash_password(password)
    user = await User.create(email=email, hashed_password=hashed_password)
    return {"status": "success", "user_id": user.id}

@router.delete("/{user_id}/")
async def delete_user(user_id: int):
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await user.delete()
    return {"status": "success", "message": "User deleted"}
 
@router.get("/{user_id}/")
async def get_user(user_id: int):
    """
    Получить данные пользователя по его ID.
    """
    user = await User.filter(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "email": user.email,
        
    }