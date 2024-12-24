from fastapi import Request

def get_rabbitmq_connection(request: Request):
    return request.app.state.rabbitmq_connection
