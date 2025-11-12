"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class AlertCreate(BaseModel):
    """Schema for creating an alert from proxy"""
    session_id: str
    client_ip: str
    upstream_ip: str
    timestamp: float
    heuristic: str
    bytes: int
    recent_samples: List[Dict] = Field(default_factory=list)
    session_stats: Optional[Dict] = None


class AlertResponse(BaseModel):
    """Schema for alert response"""
    id: int
    alert_id: str
    session_id: Optional[str]
    timestamp: datetime
    event_type: str
    event_data: Dict
    detection_methods: List[str]
    severity: str
    ml_score: Optional[float]
    rule_reasons: Optional[List[str]]
    status: str
    contained: bool
    forensic_hash: Optional[str]
    blockchain_tx_hash: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ContainRequest(BaseModel):
    """Schema for containment request"""
    session_id: str
    reason: Optional[str] = None


class ContainResponse(BaseModel):
    """Schema for containment response"""
    success: bool
    session_id: str
    message: str


class HealthResponse(BaseModel):
    """Schema for health check"""
    status: str
    timestamp: float

