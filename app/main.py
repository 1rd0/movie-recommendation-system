from fastapi import FastAPI
from app.config import init_db, close_db
from app.rabbitmq import init_rabbitmq, close_rabbitmq

from app.users import router as users_router
from app.history import router as history_router
from app.profile import router as profile_router
from app.auth import router as auth_router

app = FastAPI()

@app.on_event("startup")
async def startup():
    await init_db()
    await init_rabbitmq(app)

@app.on_event("shutdown")
async def shutdown():
    await close_db()
    await close_rabbitmq(app)

app.include_router(users_router, tags=["Users"])
app.include_router(history_router, tags=["History"])
app.include_router(profile_router, tags=["Profile"])
app.include_router(auth_router, tags=["Auth"])
