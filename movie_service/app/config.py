# app/config.py

DATABASE_URL = "postgresql://postgres:postgres@localhost:5433/postgres"
RABBITMQ_URL = "amqp://rmuser:rmpassword@localhost:5672/"
# app/config.py
TORTOISE_ORM = {
    "connections": {
        "default": "postgres://postgres:postgres@localhost:5432/movies_db"  # Укажите ваши реальные параметры БД
    },
    "apps": {
        "models": {
            "models": ["app.models", "aerich.models"],  # Если используете aerich для миграций
            "default_connection": "default",
        }
    },
}
