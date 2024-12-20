# auth_service/app/config.py
DATABASE_URL = "postgresql://postgres:postgres@localhost:5433/postgres"
RABBITMQ_URL = "amqp://rmuser:rmpassword@localhost:5672/"
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
# auth_service/app/config.py
TORTOISE_ORM = {
    "connections": {"default": "postgres://postgres:postgres@localhost:5432/auth_db"},
    "apps": {
        "models": {
            "models": ["app.models", "aerich.models"],  # Если используете aerich для миграций
            "default_connection": "default",
        }
    },
}
