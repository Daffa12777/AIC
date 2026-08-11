"""Konfigurasi aplikasi backend AlumiSight AI."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "AlumiSight AI"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"

    DATABASE_URL: str = "sqlite:///./dev.db"
    UPLOAD_DIR: str = "./storage"

    DEFAULT_FORECAST_HORIZON_DAYS: int = 30
    DEFAULT_ENERGY_TARIFF: float = 1400.0

    # Origin frontend yang diizinkan mengakses API.
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
