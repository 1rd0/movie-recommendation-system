# main.py
from fastapi import FastAPI
from database import init_db_and_rabbitmq, close_db_and_rabbitmq
from users import router as users_router 
from history import router as history_router 
from profile import router as profile_router
app = FastAPI()

@app.on_event("startup")
async def startup():
    print("Application is starting...")
    await init_db_and_rabbitmq(app)
    print("Startup completed.")

@app.on_event("shutdown")
async def shutdown():
    print("Shutting down...")
    await close_db_and_rabbitmq(app)
    print("Shutdown complete.")

app.include_router(users_router, tags=["Users"])
app.include_router(history_router, tags=["History"])
app.include_router(profile_router, tags=["Profile"]) 
from auth import router as auth_router

app.include_router(auth_router, tags=["Auth"])
