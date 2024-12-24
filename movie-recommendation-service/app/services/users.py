# app/services/users.py
import aiohttp
from fastapi import HTTPException
from app.config import USER_SERVICE_URL,EMEIL_SERVICE_URL

async def get_user_history(user_id: int):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{USER_SERVICE_URL}/users/{user_id}/history/") as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail="Failed to fetch user history")
            history = await response.json()

    if "data" not in history or not isinstance(history["data"], list):
        raise HTTPException(status_code=500, detail="Invalid user history format")

    return history["data"]
 
async def get_user_email(user_id: int) -> str:
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{EMEIL_SERVICE_URL}/users/{user_id}/") as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail="Failed to fetch user data")
            user_data = await response.json()

    if "email" not in user_data:
        raise HTTPException(status_code=500, detail="Invalid user data format")

    return user_data["email"]
