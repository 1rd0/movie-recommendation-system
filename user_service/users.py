# users.py
from fastapi import APIRouter, HTTPException, Depends
from dependencies import get_db_pool
import hashlib

router = APIRouter()

def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

@router.post("/users/")
async def create_user(email: str, password: str, db_pool=Depends(get_db_pool)):
    if not db_pool:
        print("Database pool is not initialized!")
        raise HTTPException(
            status_code=500, 
            detail="Database pool not initialized. Ensure database is running and connection settings are correct."
        )
    try:
        async with db_pool.acquire() as connection:
            hashed_password = hash_password(password)
            user_id = await connection.fetchval(
                "INSERT INTO users (email, hashed_password) VALUES ($1, $2) RETURNING id",
                email, hashed_password
            )
            return {"status": "success", "user_id": user_id}
    except Exception as e:
        print(f"Error during user creation: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.delete("/users/{user_id}/")
async def delete_user(user_id: int, db_pool=Depends(get_db_pool)):
    if not db_pool:
        raise HTTPException(
            status_code=500, 
            detail="Database pool not initialized. Ensure database is running and connection settings are correct."
        )
    try:
        async with db_pool.acquire() as connection:
            result = await connection.execute("DELETE FROM users WHERE id = $1", user_id)
            if result == "DELETE 0":
                raise HTTPException(status_code=404, detail="User not found")
        return {"status": "success", "message": "User deleted"}
    except Exception as e:
        print(f"Error during user deletion: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
