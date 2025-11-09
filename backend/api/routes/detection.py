"""
Detection API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from backend.models.database import get_db, get_mongo_db
from backend.models.alert import Alert, AlertSeverity, AuditLog
from backend.models.user import User
from backend.auth.dependencies import get_current_active_user
from backend.services.detection import DetectionService
from backend.services.celery_tasks import process_event_async

router = APIRouter()


class EventRequest(BaseModel):
    """VNC event request model"""
    event_type: str
    timestamp: Optional[float] = None
    data: Dict[str, Any]


class DetectionResponse(BaseModel):
    """Detection response model"""
    alert_id: Optional[str] = None
    is_alert: bool
    detection_methods: list
    reasons: list
    severity: Optional[str] = None
    ml_score: Optional[float] = None
    dl_score: Optional[float] = None


@router.post("/event", response_model=DetectionResponse)
async def process_event(
    event: EventRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Process a VNC event for detection"""
    # Use current timestamp if not provided
    timestamp = event.timestamp or datetime.utcnow().timestamp()
    
    # Prepare event data
    event_data = {
        "event_type": event.event_type,
        "timestamp": timestamp,
        **event.data
    }
    
    # Store in MongoDB for raw log storage
    mongo_db = get_mongo_db()
    mongo_db.events.insert_one({
        "event_type": event.event_type,
        "timestamp": datetime.fromtimestamp(timestamp),
        "data": event.data,
        "user_id": current_user.id,
        "created_at": datetime.utcnow()
    })
    
    # Process detection asynchronously
    # In production, use Celery task
    try:
        detection_service = DetectionService()
        result = detection_service.process_event(event_data)
        
        if result.get("is_alert"):
            # Create alert in database
            alert = Alert(
                alert_id=result["alert_id"],
                timestamp=datetime.fromtimestamp(timestamp),
                event_type=event.event_type,
                event_data=event.data,
                detection_methods=result.get("detection_methods", []),
                severity=AlertSeverity(result.get("severity", "medium")),
                ml_score=result.get("ml_score"),
                dl_score=result.get("dl_score"),
                rule_reasons=result.get("reasons", []),
                status="open",
                contained=False
            )
            db.add(alert)
            
            # Audit log
            audit = AuditLog(
                user_id=current_user.id,
                action="detection_alert",
                resource_type="alert",
                details={"alert_id": result["alert_id"], "event_type": event.event_type}
            )
            db.add(audit)
            db.commit()
        
        return DetectionResponse(
            alert_id=result.get("alert_id"),
            is_alert=result.get("is_alert", False),
            detection_methods=result.get("detection_methods", []),
            reasons=result.get("reasons", []),
            severity=result.get("severity"),
            ml_score=result.get("ml_score"),
            dl_score=result.get("dl_score")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Detection error: {str(e)}"
        )


@router.post("/event/async")
async def process_event_async_endpoint(
    event: EventRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Process event asynchronously using Celery"""
    timestamp = event.timestamp or datetime.utcnow().timestamp()
    
    event_data = {
        "event_type": event.event_type,
        "timestamp": timestamp,
        **event.data
    }
    
    # Store in MongoDB
    mongo_db = get_mongo_db()
    mongo_db.events.insert_one({
        "event_type": event.event_type,
        "timestamp": datetime.fromtimestamp(timestamp),
        "data": event.data,
        "user_id": current_user.id,
        "created_at": datetime.utcnow()
    })
    
    # Queue Celery task
    task = process_event_async.delay(event_data, current_user.id)
    
    return {
        "task_id": task.id,
        "status": "queued",
        "message": "Event queued for processing"
    }

