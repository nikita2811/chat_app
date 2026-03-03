from fastapi_mail import FastMail, ConnectionConfig
from pathlib import Path
from app.core.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_PORT=settings.MAIL_PORT,

    MAIL_STARTTLS=True,   # REQUIRED
    MAIL_SSL_TLS=False,   # REQUIRED

    USE_CREDENTIALS=True,
   
    TEMPLATE_FOLDER=Path(__file__).parent.parent / "templates"
)

fm = FastMail(conf)
