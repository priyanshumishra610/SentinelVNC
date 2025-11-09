"""
Database connection and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from pymongo import MongoClient
from pymongo.database import Database
from backend.config import settings

# PostgreSQL
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Get PostgreSQL database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# MongoDB
_mongo_client: MongoClient = None
_mongo_db: Database = None


def get_mongo_client() -> MongoClient:
    """Get MongoDB client"""
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoClient(settings.MONGODB_URL)
    return _mongo_client


def get_mongo_db() -> Database:
    """Get MongoDB database"""
    global _mongo_db
    if _mongo_db is None:
        client = get_mongo_client()
        _mongo_db = client[settings.MONGODB_DB]
    return _mongo_db


def close_mongo_connection():
    """Close MongoDB connection"""
    global _mongo_client
    if _mongo_client:
        _mongo_client.close()
        _mongo_client = None

