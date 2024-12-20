from fastapi import APIRouter, HTTPException
from tortoise.exceptions import DoesNotExist
from app.models import User, UserProfile

router = APIRouter()

@router.post("/users/{user_id}/profile/")
async def create_profile(user_id: int, name: str, preferences: str = None):
    try:
        user = await User.get(id=user_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")

    # Создаем профиль
    await UserProfile.create(user=user, name=name, preferences=preferences)
    return {"status": "success", "message": "User profile created"}
