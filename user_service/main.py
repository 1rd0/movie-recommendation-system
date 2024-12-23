from fastapi import FastAPI
from config import init_db, close_db
from app.routers.users import router as users_router
from app.routers.auth import router as auth_router
from app.routers.profile import router as profile_router

app = FastAPI()

@app.on_event("startup")
async def startup():
    await init_db()

@app.on_event("shutdown")
async def shutdown():
    await close_db()

app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(profile_router, prefix="/profile", tags=["Profiles"])
