from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "ECOA - Monitor de Notícias"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # MySQL Database (Railway)
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_DATABASE: str = "ecoa"
    DATABASE_URL: Optional[str] = None

    @property
    def mysql_url(self) -> str:
        if self.DATABASE_URL:
            # Railway provides DATABASE_URL
            return self.DATABASE_URL.replace("mysql://", "mysql+pymysql://")
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"

    @property
    def async_mysql_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL.replace("mysql://", "mysql+aiomysql://")
        return f"mysql+aiomysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"

    # JWT Authentication
    JWT_SECRET_KEY: str = "your-super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Redis (for Celery)
    REDIS_URL: str = "redis://localhost:6379/0"

    # Scraping
    SCRAPE_INTERVAL_MINUTES: int = 30

    # Plan limits
    FREE_PLAN_TERM_LIMIT: int = 3
    PRO_PLAN_TERM_LIMIT: int = 100

    # CORS
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "https://*.railway.app",
    ]

    class Config:
        env_file = ".env"
        extra = "allow"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
