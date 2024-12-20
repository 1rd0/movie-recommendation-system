# app/main.py

from fastapi import FastAPI
import logging

from app.routers import movies
from app.services.database import init_db, close_db
from app.services.rabbitmq import init_rabbitmq, close_rabbitmq

app = FastAPI()

@app.on_event("startup")
async def startup():
    logging.info("Initializing resources...")
    await init_db(app)
    await init_rabbitmq(app)

@app.on_event("shutdown")
async def shutdown():
    logging.info("Releasing resources...")
    await close_db(app)
    await close_rabbitmq(app)

app.include_router(movies.router)
