import asyncio
from fastapi import FastAPI
from app.consumers import start_consumer

app = FastAPI(title="Notification Service")

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(start_consumer())
