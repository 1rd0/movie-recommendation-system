from fastapi import APIRouter, HTTPException, Depends
from dependencies import get_db_pool

router = APIRouter()

@router.post("/users/{user_id}/profile/")
async def create_profile(user_id: int, name: str, preferences: str = None, db_pool=Depends(get_db_pool)):
    if not db_pool:
        raise HTTPException(
            status_code=500,
            detail="Database pool not initialized. Ensure database is running and connection settings are correct."
        )
    try:
        async with db_pool.acquire() as connection:
            await connection.execute(
                "INSERT INTO user_profiles (user_id, name, preferences) VALUES ($1, $2, $3)",
                user_id, name, preferences
            )
        return {"status": "success", "message": "User profile created"}
    except Exception as e:
        # Логируем ошибку (опционально)
        print(f"Error during profile creation: {e}")
        # Выбрасываем HTTPException с подробностью ошибки
        raise HTTPException(status_code=500, detail="Internal Server Error")
