from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_ENV: str = "development"
    DATABASE_URL: str
    REDIS_URL: str
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET: str
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4-turbo"
    WEAVIATE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    class Config:
        env_file = ".env"
settings = Settings()
