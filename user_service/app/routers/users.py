from fastapi import APIRouter, HTTPException
from app.models import User
import hashlib
from fastapi import APIRouter, HTTPException
from app.models import User, UserProfile
from schemas import UserProfileCreate,UserCreate, UserResponse
router = APIRouter()
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate):
    hashed_password = hash_password(user.password)
    try:
        new_user = await User.create(email=user.email, hashed_password=hashed_password)
    except Exception as e:
        raise HTTPException(status_code=400, detail="User already exists")
    return new_user
@router.delete("/{user_id}/")
async def delete_user(user_id: int):
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await user.delete()
    return {"status": "success", "message": "User deleted"}
 
@router.get("/{user_id}/", response_model=UserResponse)
async def get_user(user_id: int):
    user = await User.filter(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
