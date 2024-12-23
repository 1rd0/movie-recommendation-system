from fastapi import APIRouter, HTTPException
from app.models import User, UserProfile

router = APIRouter()

@router.post("/{user_id}/")
async def create_profile(user_id: int, name: str, preferences: str = None):
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    profile = await UserProfile.create(user=user, name=name, preferences=preferences)
    return {"status": "success", "profile_id": profile.id}
