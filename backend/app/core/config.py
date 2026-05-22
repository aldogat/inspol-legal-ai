import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./test.db"
    REDIS_URL: str = "redis://localhost:6379"
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "test"
    OPENAI_API_KEY: str
    WEAVIATE_URL: str = "http://localhost:8080"
    JWT_SECRET: str = "supersecretkey"
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        env_origins = os.getenv("BACKEND_CORS_ORIGINS")
        if env_origins:
            self.BACKEND_CORS_ORIGINS = [origin.strip() for origin in env_origins.split(",")]

settings = Settings()
