from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "ECOA - Monitor de Notícias"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # Supabase
    SUPABASE_URL: str = "https://cqrpbiepyeypbkizwacu.supabase.co"
    SUPABASE_ANON_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNxcnBiaWVweWV5cGJraXp3YWN1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU3MDA0MTksImV4cCI6MjA3MTI3NjQxOX0.Iyy2W5tw0-40sQdRfFJTfwYij4iUl8-KoUlg39u7kOE"

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
    ]

    class Config:
        env_file = ".env"
        extra = "allow"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
