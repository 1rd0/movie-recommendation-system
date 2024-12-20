# auth_service/app/main.py
from fastapi import FastAPI
from app.services.database import init_db, close_db
from app.services.rabbitmq import init_rabbitmq, close_rabbitmq
from app.routers import auth, users

app = FastAPI(title="Auth Service")

@app.on_event("startup")
async def startup():
    await init_db(app)
    await init_rabbitmq(app)

@app.on_event("shutdown")
async def shutdown():
    await close_db(app)
    await close_rabbitmq(app)

app.include_router(auth.router, tags=["Auth"])
app.include_router(users.router, tags=["Users"])
