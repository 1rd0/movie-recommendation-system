# app/main.py

from fastapi import FastAPI
from routers import recommendations

app = FastAPI()

app.include_router(recommendations.router, tags=["Recommendations"])
