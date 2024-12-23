from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    RABBITMQ_URL: str = "amqp://rmuser:rmpassword@localhost:5672/"
    SMTP_SERVER: str = "smtp.mail.ru"  # Используйте сервер вашей почты
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = "dimrabdel@mail.ru"  # Ваша почта
    SMTP_PASSWORD: str = "Df0B9bcj3vyBnsEAmVJK"        # Пароль от почты
    FROM_EMAIL: str = "dimrabdel@mail.ru"

    class Config:
        env_file = ".env"

settings = Settings()
