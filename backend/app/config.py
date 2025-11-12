"""
Configuration loader reading from .env
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Application
    APP_NAME: str = "SentinelVNC"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./sentinelvnc.db"
    )
    
    # JWT
    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY",
        "change-me-in-production-use-strong-random-key"
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))
    
    # Redis (for Celery)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # ML Model
    ML_MODEL_PATH: str = os.getenv("ML_MODEL_PATH", "models/detection_model.pkl")
    
    # Alert URL (for proxy)
    ALERT_URL: str = os.getenv("ALERT_URL", "http://localhost:8000/api/v1/alerts")
    
    # Containment
    AUTO_CONTAIN_ON_ALERT: bool = os.getenv("AUTO_CONTAIN_ON_ALERT", "false").lower() == "true"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

