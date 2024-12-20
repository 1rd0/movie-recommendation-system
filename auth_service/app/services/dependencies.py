# auth_service/app/services/dependencies.py
from fastapi import Request

def get_db_pool(request: Request):
    return request.app.state.db_pool
