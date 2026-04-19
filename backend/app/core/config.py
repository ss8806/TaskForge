from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# .envファイルの絶対パスを設定
BACKEND_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BACKEND_DIR / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE) if ENV_FILE.exists() else ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str = "postgresql://postgres:password@localhost:5433/taskforge"
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    JWT_SECRET_KEY: str = Field(
        min_length=64,
        description="JWT secret key - must be at least 64 characters. Generate with: openssl rand -base64 64",
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    OPENAI_API_KEY: str = ""  # Required for AI features
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"


settings = Settings()
