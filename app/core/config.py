# app/core/config.py
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    APP_NAME: str = "Chat App"

    SECRET_KEY: str
    ALGORITHM: str = "HS256"

    ACCESS_EXPIRE_MIN: int
    REFRESH_EXPIRE_DAYS: int

    MONGO_URL: str
    REDIS_URL: str

    MAIL_USERNAME:str
    MAIL_PASSWORD:str
    MAIL_FROM:str
    MAIL_SERVER:str
    MAIL_PORT:int =587,

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
