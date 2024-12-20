from fastapi import APIRouter, HTTPException
import hashlib
from tortoise.exceptions import DoesNotExist
from app.models import User

router = APIRouter()

def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

@router.post("/users/")
async def create_user(email: str, password: str):
    hashed_password = hash_password(password)
    user = await User.create(email=email, hashed_password=hashed_password)
    return {"status": "success", "user_id": user.id}

@router.delete("/users/{user_id}/")
async def delete_user(user_id: int):
    try:
        user = await User.get(id=user_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")
    await user.delete()
    return {"status": "success", "message": "User deleted"}
