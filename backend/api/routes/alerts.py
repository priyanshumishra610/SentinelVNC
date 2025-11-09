"""
Alert management routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
from backend.models.database import get_db
from backend.models.alert import Alert, AlertSeverity, DetectionMethod, AuditLog
from backend.models.user import User
from backend.auth.dependencies import get_current_active_user, require_role
from backend.models.user import UserRole

router = APIRouter()


class AlertResponse(BaseModel):
    """Alert response model"""
    id: int
    alert_id: str
    timestamp: str
    event_type: str
    event_data: dict
    detection_methods: List[str]
    severity: str
    ml_score: Optional[float]
    dl_score: Optional[float]
    rule_reasons: Optional[List[str]]
    status: str
    contained: bool
    forensic_hash: Optional[str]
    blockchain_tx_hash: Optional[str]
    created_at: str


class AlertUpdate(BaseModel):
    """Alert update model"""
    status: Optional[str] = None
    assigned_to: Optional[int] = None
    notes: Optional[str] = None
    contained: Optional[bool] = None


@router.get("/", response_model=List[AlertResponse])
async def list_alerts(
    skip: int = 0,
    limit: int = 100,
    severity: Optional[AlertSeverity] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List alerts with filters"""
    query = db.query(Alert)
    
    # Apply filters
    if severity:
        query = query.filter(Alert.severity == severity)
    if status:
        query = query.filter(Alert.status == status)
    if start_date:
        query = query.filter(Alert.timestamp >= start_date)
    if end_date:
        query = query.filter(Alert.timestamp <= end_date)
    
    # Order by timestamp descending
    alerts = query.order_by(desc(Alert.timestamp)).offset(skip).limit(limit).all()
    
    return [
        AlertResponse(
            id=a.id,
            alert_id=a.alert_id,
            timestamp=a.timestamp.isoformat(),
            event_type=a.event_type,
            event_data=a.event_data,
            detection_methods=a.detection_methods,
            severity=a.severity.value,
            ml_score=a.ml_score,
            dl_score=a.dl_score,
            rule_reasons=a.rule_reasons,
            status=a.status,
            contained=a.contained,
            forensic_hash=a.forensic_hash,
            blockchain_tx_hash=a.blockchain_tx_hash,
            created_at=a.created_at.isoformat()
        )
        for a in alerts
    ]


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get alert by ID"""
    alert = db.query(Alert).filter(Alert.alert_id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    return AlertResponse(
        id=alert.id,
        alert_id=alert.alert_id,
        timestamp=alert.timestamp.isoformat(),
        event_type=alert.event_type,
        event_data=alert.event_data,
        detection_methods=alert.detection_methods,
        severity=alert.severity.value,
        ml_score=alert.ml_score,
        dl_score=alert.dl_score,
        rule_reasons=alert.rule_reasons,
        status=alert.status,
        contained=alert.contained,
        forensic_hash=alert.forensic_hash,
        blockchain_tx_hash=alert.blockchain_tx_hash,
        created_at=alert.created_at.isoformat()
    )


@router.put("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: str,
    alert_data: AlertUpdate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.ANALYST])),
    db: Session = Depends(get_db)
):
    """Update alert (Admin/Analyst only)"""
    alert = db.query(Alert).filter(Alert.alert_id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    # Update fields
    if alert_data.status is not None:
        alert.status = alert_data.status
    
    if alert_data.assigned_to is not None:
        # Verify user exists
        user = db.query(User).filter(User.id == alert_data.assigned_to).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        alert.assigned_to = alert_data.assigned_to
    
    if alert_data.notes is not None:
        alert.notes = alert_data.notes
    
    if alert_data.contained is not None:
        alert.contained = alert_data.contained
        if alert_data.contained:
            alert.contained_at = datetime.utcnow()
    
    alert.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(alert)
    
    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        action="update_alert",
        resource_type="alert",
        resource_id=alert.id,
        details={"alert_id": alert.alert_id, "changes": alert_data.dict(exclude_unset=True)}
    )
    db.add(audit)
    db.commit()
    
    return AlertResponse(
        id=alert.id,
        alert_id=alert.alert_id,
        timestamp=alert.timestamp.isoformat(),
        event_type=alert.event_type,
        event_data=alert.event_data,
        detection_methods=alert.detection_methods,
        severity=alert.severity.value,
        ml_score=alert.ml_score,
        dl_score=alert.dl_score,
        rule_reasons=alert.rule_reasons,
        status=alert.status,
        contained=alert.contained,
        forensic_hash=alert.forensic_hash,
        blockchain_tx_hash=alert.blockchain_tx_hash,
        created_at=alert.created_at.isoformat()
    )


@router.get("/stats/summary")
async def get_alert_stats(
    days: int = Query(7, ge=1, le=365),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get alert statistics"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    total = db.query(Alert).filter(Alert.timestamp >= start_date).count()
    by_severity = {}
    by_status = {}
    by_method = {}
    
    alerts = db.query(Alert).filter(Alert.timestamp >= start_date).all()
    
    for alert in alerts:
        # By severity
        severity = alert.severity.value
        by_severity[severity] = by_severity.get(severity, 0) + 1
        
        # By status
        status = alert.status
        by_status[status] = by_status.get(status, 0) + 1
        
        # By detection method
        for method in alert.detection_methods:
            by_method[method] = by_method.get(method, 0) + 1
    
    return {
        "total": total,
        "by_severity": by_severity,
        "by_status": by_status,
        "by_method": by_method,
        "period_days": days
    }

