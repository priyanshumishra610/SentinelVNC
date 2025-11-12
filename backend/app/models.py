"""
SQLAlchemy models for SentinelVNC
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import enum
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.config import settings

Base = declarative_base()

# Create engine and session
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class AlertSeverity(str, enum.Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class Alert(Base):
    """Alert model for detected threats"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String(50), unique=True, index=True, nullable=False)
    session_id = Column(String(100), index=True, nullable=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # Event details
    event_type = Column(String(50), nullable=False, index=True)
    event_data = Column(JSON, nullable=False)
    
    # Detection
    detection_methods = Column(JSON, nullable=False)  # List of strings
    severity = Column(Enum(AlertSeverity), default=AlertSeverity.MEDIUM, nullable=False, index=True)
    
    # ML scores
    ml_score = Column(Float, nullable=True)
    rule_reasons = Column(JSON, nullable=True)  # List of strings
    
    # Explainability
    shap_values = Column(JSON, nullable=True)
    
    # Status
    status = Column(String(20), default="open", nullable=False, index=True)
    contained = Column(Boolean, default=False, nullable=False)
    contained_at = Column(DateTime, nullable=True)
    
    # Forensics
    forensic_hash = Column(String(64), nullable=True, index=True)
    blockchain_tx_hash = Column(String(66), nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Alert(id={self.id}, alert_id={self.alert_id}, severity={self.severity})>"


class Forensic(Base):
    """Forensic bundle model"""
    __tablename__ = "forensics"
    
    id = Column(Integer, primary_key=True, index=True)
    forensic_id = Column(String(50), unique=True, index=True, nullable=False)
    alert_id = Column(String(50), index=True, nullable=False)
    merkle_root = Column(String(64), nullable=False, index=True)
    artifacts = Column(JSON, nullable=False)  # List of artifact hashes
    proof = Column(JSON, nullable=True)  # Merkle proof
    blockchain_tx_hash = Column(String(66), nullable=True, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Forensic(id={self.id}, forensic_id={self.forensic_id})>"

