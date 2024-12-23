from fastapi import FastAPI
from app.config import init_db, close_db
from app.rabbitmq import init_rabbitmq, close_rabbitmq

 
from app.history import router as history_router
 

app = FastAPI()

@app.on_event("startup")
async def startup():
    await init_db()
    await init_rabbitmq(app)

@app.on_event("shutdown")
async def shutdown():
    await close_db()
    await close_rabbitmq(app)

 
app.include_router(history_router, tags=["History"])
