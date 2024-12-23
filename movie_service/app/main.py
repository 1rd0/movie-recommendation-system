# app/main.py
from fastapi import FastAPI
from tortoise import Tortoise
from app.config import TORTOISE_ORM
from app.routers import movies

from app.services.rabbitmq import init_rabbitmq, close_rabbitmq

app = FastAPI(title="Movie Service with Tortoise")

@app.on_event("startup")
async def startup():
    # Инициализация Tortoise ORM
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()
    await init_rabbitmq(app)

@app.on_event("shutdown")
async def shutdown():
    await Tortoise.close_connections()
    await close_rabbitmq(app)

app.include_router(movies.router)
 