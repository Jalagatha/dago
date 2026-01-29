from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Food & Parcel Delivery API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: str = "*"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
