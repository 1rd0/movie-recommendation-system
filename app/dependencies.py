from fastapi import Request

# Если нужно будет что-то зависимое, например RabbitMQ, можно получить так:
def get_rabbitmq_connection(request: Request):
    return request.app.state.rabbitmq_connection
