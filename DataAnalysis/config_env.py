from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


@dataclass(slots=True)
class BaseConfig:
    app_name: str = "DataPulse 大数据AI分析系统"
    app_version: str = "1.0.0"
    env: str = "development"
    host: str = "0.0.0.0"
    port: int = 8000
    secret_key: str = "dev-secret-change-me"
    app_secret: str = "dev-app-secret"
    cors_origins: list[str] = field(default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"])
    log_dir: Path = BASE_DIR / "logs"
    database_url: str = f"sqlite:///{BASE_DIR / 'datapulse_dev.db'}"
    ai_provider: str = "local-demo"
    ai_default_model: str = "DataPulse-Demo-Agent"
    scheduler_enabled: bool = True


class DevelopmentConfig(BaseConfig):
    def __init__(self) -> None:
        super().__init__()
        self.env = "development"
        self.database_url = os.getenv("DATABASE_URL", self.database_url)


class ProductionConfig(BaseConfig):
    def __init__(self) -> None:
        super().__init__()
        self.env = "production"
        user = os.getenv("DB_USER", "datapulse")
        password = os.getenv("DB_PASSWORD", "")
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "3306")
        db_name = os.getenv("DB_NAME", "datapulse")
        self.database_url = os.getenv(
            "DATABASE_URL",
            f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}?charset=utf8mb4",
        )
        self.secret_key = os.getenv("SECRET_KEY", self.secret_key)
        self.app_secret = os.getenv("APP_SECRET", self.app_secret)
        self.cors_origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "*").split(",") if origin.strip()]


def get_config() -> BaseConfig:
    env = os.getenv("DATAPULSE_ENV", "development").lower()
    return ProductionConfig() if env == "production" else DevelopmentConfig()


settings = get_config()
