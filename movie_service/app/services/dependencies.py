
from fastapi import Request

def get_db_pool(request: Request):
    return request.app.state.db_pool

def get_rabbitmq_connection(request: Request):
    return request.app.state.rabbitmq_connection
