"""
Celery tasks for async detection processing
"""
from celery import Celery
from backend.config import settings
from backend.services.detection import EnhancedDetectionService
from backend.models.database import get_db, SessionLocal
from backend.models.alert import Alert, AlertSeverity
from backend.models.alert import AuditLog
from backend.api.routes.websocket import broadcast_alert
from datetime import datetime
import asyncio

# Create Celery app
celery_app = Celery(
    "sentinelvnc",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes
)


@celery_app.task(name="detection.process_event")
def process_event_async(event_data: dict, user_id: int):
    """Process event asynchronously"""
    try:
        # Initialize detection service
        detection_service = EnhancedDetectionService()
        
        # Process event
        result = detection_service.process_event(event_data)
        
        if result.get("is_alert"):
            # Create alert in database
            db = SessionLocal()
            try:
                alert = Alert(
                    alert_id=result["alert_id"],
                    timestamp=datetime.fromtimestamp(event_data.get("timestamp", datetime.utcnow().timestamp())),
                    event_type=event_data.get("event_type"),
                    event_data=event_data,
                    detection_methods=result.get("detection_methods", []),
                    severity=AlertSeverity(result.get("severity", "medium")),
                    ml_score=result.get("ml_score"),
                    dl_score=result.get("dl_score"),
                    rule_reasons=result.get("reasons", []),
                    status="open",
                    contained=False,
                    forensic_hash=result.get("forensic_hash")
                )
                db.add(alert)
                
                # Audit log
                audit = AuditLog(
                    user_id=user_id,
                    action="detection_alert",
                    resource_type="alert",
                    details={"alert_id": result["alert_id"], "event_type": event_data.get("event_type")}
                )
                db.add(audit)
                db.commit()
                
                # Broadcast via WebSocket
                alert_data = {
                    "alert_id": result["alert_id"],
                    "timestamp": alert.timestamp.isoformat(),
                    "event_type": event_data.get("event_type"),
                    "severity": result.get("severity"),
                    "detection_methods": result.get("detection_methods", []),
                    "reasons": result.get("reasons", [])
                }
                asyncio.run(broadcast_alert(alert_data))
                
            finally:
                db.close()
        
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@celery_app.task(name="detection.retrain_model")
def retrain_model_async():
    """Retrain ML model asynchronously"""
    try:
        # Import training function
        import sys
        from pathlib import Path
        sys.path.append(str(Path(__file__).parent.parent.parent))
        from train_model import train_model
        
        # Train model
        train_model()
        
        return {
            "success": True,
            "message": "Model retrained successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@celery_app.task(name="detection.archive_old_logs")
def archive_old_logs():
    """Archive logs older than retention period"""
    try:
        from backend.config import settings
        from backend.models.database import get_mongo_db
        from datetime import datetime, timedelta
        
        mongo_db = get_mongo_db()
        cutoff_date = datetime.utcnow() - timedelta(days=settings.LOG_RETENTION_DAYS)
        
        # Archive old events
        result = mongo_db.events.update_many(
            {"timestamp": {"$lt": cutoff_date}},
            {"$set": {"archived": True, "archived_at": datetime.utcnow()}}
        )
        
        return {
            "success": True,
            "archived_count": result.modified_count
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

