from fastapi import FastAPI
from tortoise import Tortoise
from app.config import TORTOISE_ORM
from routers import recommendations
 
app = FastAPI(title="Recommendation Service with Tortoise")

@app.on_event("startup")
async def startup():
    
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()
    

@app.on_event("shutdown")
async def shutdown():
    await Tortoise.close_connections()
 
app.include_router(recommendations.router, tags=["Recommendations"])
