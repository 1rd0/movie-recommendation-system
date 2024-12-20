# auth_service/app/services/users_service.py
from fastapi import HTTPException
from app.services.auth_service import hash_password

async def create_user_in_db(db_pool, email: str, password: str):
    async with db_pool.acquire() as conn:
        # Проверяем, что пользователь не существует
        existing = await conn.fetchrow("SELECT id FROM user WHERE email = $1", email)
        if existing:
            raise HTTPException(status_code=400, detail="User already exists")
        hashed = hash_password(password)
        user_id = await conn.fetchval(
            "INSERT INTO user (email, hashed_password) VALUES ($1, $2) RETURNING id",
            email, hashed
        )
        return user_id

async def delete_user_in_db(db_pool, user_id: int):
    async with db_pool.acquire() as conn:
        result = await conn.execute("DELETE FROM user WHERE id=$1", user_id)
        if result == "DELETE 0":
            return False
        return True
