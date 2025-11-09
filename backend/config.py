"""
Configuration management for SentinelVNC v2
"""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "SentinelVNC v2"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production-use-strong-random-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # JWT
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ALGORITHM: str = ALGORITHM
    
    # 2FA
    TOTP_ISSUER: str = "SentinelVNC"
    TOTP_VALIDITY_WINDOW: int = 1
    
    # Database - PostgreSQL
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "sentinel")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "sentinel")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "sentinelvnc")
    DATABASE_URL: Optional[str] = None
    
    # Database - MongoDB
    MONGODB_HOST: str = os.getenv("MONGODB_HOST", "localhost")
    MONGODB_PORT: int = int(os.getenv("MONGODB_PORT", "27017"))
    MONGODB_USER: str = os.getenv("MONGODB_USER", "sentinel")
    MONGODB_PASSWORD: str = os.getenv("MONGODB_PASSWORD", "sentinel")
    MONGODB_DB: str = os.getenv("MONGODB_DB", "sentinelvnc_logs")
    MONGODB_URL: Optional[str] = None
    
    # Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD", None)
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_URL: Optional[str] = None
    
    # Celery
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    
    # Encryption
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "change-me-32-char-key-here!")
    KEY_ROTATION_DAYS: int = 30
    
    # Data Retention
    LOG_RETENTION_DAYS: int = 90
    
    # Detection
    ML_MODEL_PATH: str = "models/detection_model.pkl"
    DL_MODEL_PATH: str = "models/dl_anomaly_model.h5"
    ML_THRESHOLD: float = 0.5
    DL_THRESHOLD: float = 0.5
    
    # Blockchain
    BLOCKCHAIN_NODE_URL: str = os.getenv("BLOCKCHAIN_NODE_URL", "http://localhost:8545")
    MERKLE_BATCH_SIZE: int = 100
    
    # ELK Stack
    ELASTICSEARCH_HOST: str = os.getenv("ELASTICSEARCH_HOST", "localhost")
    ELASTICSEARCH_PORT: int = int(os.getenv("ELASTICSEARCH_PORT", "9200"))
    ELASTICSEARCH_URL: Optional[str] = None
    
    # Email/Slack Alerts
    SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST", None)
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER", None)
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD", None)
    SLACK_WEBHOOK_URL: Optional[str] = os.getenv("SLACK_WEBHOOK_URL", None)
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 15
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Build connection URLs
        self.DATABASE_URL = (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
        
        if self.MONGODB_USER and self.MONGODB_PASSWORD:
            self.MONGODB_URL = (
                f"mongodb://{self.MONGODB_USER}:{self.MONGODB_PASSWORD}"
                f"@{self.MONGODB_HOST}:{self.MONGODB_PORT}/{self.MONGODB_DB}"
            )
        else:
            self.MONGODB_URL = f"mongodb://{self.MONGODB_HOST}:{self.MONGODB_PORT}/{self.MONGODB_DB}"
        
        if self.REDIS_PASSWORD:
            self.REDIS_URL = f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        else:
            self.REDIS_URL = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        
        self.CELERY_BROKER_URL = self.REDIS_URL
        self.CELERY_RESULT_BACKEND = self.REDIS_URL
        
        self.ELASTICSEARCH_URL = f"http://{self.ELASTICSEARCH_HOST}:{self.ELASTICSEARCH_PORT}"


# Global settings instance
settings = Settings()

