import smtplib
from email.mime.text import MIMEText
from app.config import settings

async def send_email(to_email: str, subject: str, body: str):
    """
    Отправляет email с рекомендациями фильмов.
    """
    try:
        msg = MIMEText(body, "plain")
        msg["Subject"] = subject
        msg["From"] = settings.FROM_EMAIL
        msg["To"] = to_email

        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()  # Шифрование соединения
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(msg)
            print(f"Email успешно отправлен на {to_email}")
    except Exception as e:
        print(f"Ошибка отправки email: {e}")
