# auth_service/app/routers/users.py
from fastapi import APIRouter, Depends, HTTPException
from app.models import UserCreate
from app.services.dependencies import get_db_pool
from app.services.users_service import create_user_in_db, delete_user_in_db

router = APIRouter()

@router.post("/users/")
async def create_user(user: UserCreate, db_pool=Depends(get_db_pool)):
    user_id = await create_user_in_db(db_pool, user.email, user.password)
    return {"status": "success", "user_id": user_id}

@router.delete("/users/{user_id}/")
async def delete_user(user_id: int, db_pool=Depends(get_db_pool)):
    deleted = await delete_user_in_db(db_pool, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "success", "message": "User deleted"}
