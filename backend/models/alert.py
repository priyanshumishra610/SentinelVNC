"""
Alert and detection models
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, Text, Enum
from sqlalchemy.sql import func
import enum
from backend.models.database import Base


class AlertSeverity(str, enum.Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DetectionMethod(str, enum.Enum):
    """Detection methods"""
    RULE_BASED = "rule_based"
    ML_BASED = "ml_based"
    DL_BASED = "dl_based"
    HYBRID = "hybrid"


class Alert(Base):
    """Alert model for detected threats"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String(50), unique=True, index=True, nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # Event details
    event_type = Column(String(50), nullable=False, index=True)
    event_data = Column(JSON, nullable=False)
    
    # Detection
    detection_methods = Column(JSON, nullable=False)  # List of DetectionMethod
    severity = Column(Enum(AlertSeverity), default=AlertSeverity.MEDIUM, nullable=False, index=True)
    
    # ML/DL scores
    ml_score = Column(Float, nullable=True)
    dl_score = Column(Float, nullable=True)
    rule_reasons = Column(JSON, nullable=True)  # List of strings
    
    # Explainability
    shap_values = Column(JSON, nullable=True)
    lime_explanation = Column(JSON, nullable=True)
    
    # Status
    status = Column(String(20), default="open", nullable=False, index=True)  # open, investigating, contained, resolved
    assigned_to = Column(Integer, nullable=True)  # User ID
    notes = Column(Text, nullable=True)
    
    # Containment
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


class AuditLog(Base):
    """Audit log for user actions"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), nullable=True)
    resource_id = Column(Integer, nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    timestamp = Column(DateTime, server_default=func.now(), nullable=False, index=True)
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, user_id={self.user_id}, action={self.action})>"

