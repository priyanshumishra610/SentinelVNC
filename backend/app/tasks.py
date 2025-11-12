"""
Celery tasks or background task stubs
"""
from celery import Celery
from backend.app.config import settings

# Create Celery app
celery_app = Celery(
    "sentinelvnc",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@celery_app.task(name="process_alert_async")
def process_alert_async(alert_data: dict):
    """
    Process alert asynchronously (stub).
    In production, this would:
    - Run additional ML analysis
    - Generate forensic bundles
    - Send notifications
    - Update dashboards
    """
    # Stub implementation
    print(f"[Celery] Processing alert: {alert_data.get('alert_id')}")
    return {"status": "processed", "alert_id": alert_data.get("alert_id")}


@celery_app.task(name="generate_forensic_bundle")
def generate_forensic_bundle_async(alert_id: str, artifacts: list):
    """
    Generate forensic bundle asynchronously.
    """
    from backend.app.forensics import create_forensic_bundle
    
    alert_data = {"alert_id": alert_id}
    bundle = create_forensic_bundle(alert_data, artifacts)
    
    return bundle


@celery_app.task(name="send_notification")
def send_notification_async(alert_id: str, severity: str):
    """
    Send notification asynchronously (stub).
    In production, this would send email/Slack notifications.
    """
    print(f"[Celery] Sending notification for alert {alert_id} (severity: {severity})")
    return {"status": "sent", "alert_id": alert_id}


# For local development without Celery, use simple function stubs
def process_alert_sync(alert_data: dict):
    """Synchronous version for local development"""
    return process_alert_async(alert_data)


def generate_forensic_bundle_sync(alert_id: str, artifacts: list):
    """Synchronous version for local development"""
    return generate_forensic_bundle_async(alert_id, artifacts)

