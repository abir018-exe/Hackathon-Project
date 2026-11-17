from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Last Mile Stabilizer"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = Field(..., description="PostgreSQL connection string")
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    
    # Security
    SECRET_KEY: str = Field(..., min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    
    # GitHub OAuth
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None
    GITHUB_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/github/callback"
    
    # AI Configuration
    AI_PROVIDER: str = "openai"
    AI_API_KEY: Optional[str] = None
    AI_MODEL: str = "gpt-4-turbo-preview"
    AI_TEMPERATURE: float = 0.1
    AI_MAX_TOKENS: int = 4000
    
    # Storage
    PROJECT_STORAGE_PATH: str = "./storage"
    MAX_UPLOAD_SIZE_MB: int = 500
    ALLOWED_ARCHIVE_EXTENSIONS: List[str] = [".zip", ".tar", ".tar.gz", ".tgz"]
    
    # Docker Sandbox
    DOCKER_ENABLED: bool = True
    DOCKER_CPU_LIMIT: float = 1.0
    DOCKER_MEMORY_LIMIT: str = "512m"
    DOCKER_TIMEOUT_SECONDS: int = 120
    DOCKER_NETWORK_DISABLED: bool = True
    
    # Celery
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/0")
    CELERY_TASK_TRACK_STARTED: bool = True
    CELERY_TASK_TIME_LIMIT: int = 300
    CELERY_WORKER_PREFETCH_MULTIPLIER: int = 1
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Sentry
    SENTRY_DSN: Optional[str] = None
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()