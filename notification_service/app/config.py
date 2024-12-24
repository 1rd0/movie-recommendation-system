from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    RABBITMQ_URL: str = "amqp://rmuser:rmpassword@localhost:5672/"
    SMTP_SERVER: str = "smtp.mail.ru"  
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = "dimrabdel@mail.ru"  
    SMTP_PASSWORD: str = "Df0B9bcj3vyBnsEAmVJK"        
    FROM_EMAIL: str = "dimrabdel@mail.ru"

    class Config:
        env_file = ".env"

settings = Settings()
