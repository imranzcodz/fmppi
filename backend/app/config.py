from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "FMPPI Backend API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    DATABASE_URL: str = "sqlite:///./fmppi.db"

    SECRET_KEY: str = "dev-secret-change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    PASSWORD_SCHEME: str = "bcrypt"  # bcrypt | argon2
    BCRYPT_ROUNDS: int = 12

    MFA_ISSUER: str = "FMPPI"
    MFA_WINDOW: int = 1

    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10 MB
    ALLOWED_IMAGE_EXTENSIONS: str = "jpg,jpeg,png,webp"
    ALLOWED_IMAGE_MIME_TYPES: str = "image/jpeg,image/png,image/webp"

    RATE_LIMIT_DEFAULT: int = 100  # requests per minute
    RATE_LIMIT_AUTH: int = 20      # requests per minute for auth endpoints

    CORS_ORIGINS: str = "*"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
