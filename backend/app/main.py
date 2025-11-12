"""
FastAPI app with /alerts POST, /contain POST, health check, OpenAPI
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
import time

from backend.app.config import settings
from backend.app.models import Base, engine, get_db, Alert, AlertSeverity
from backend.app.schemas import (
    AlertCreate, AlertResponse, ContainRequest, ContainResponse, HealthResponse
)
from backend.app.detector import detection_engine
from backend.app.forensics import create_forensic_bundle
from backend.app.auth import get_current_user, require_admin
from backend.app.tasks import process_alert_sync

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="VNC Security Layer - Exfiltration Detection and Containment",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=time.time()
    )


@app.post("/api/v1/alerts", response_model=dict)
async def create_alert(
    alert_data: AlertCreate,
    db: Session = Depends(get_db),
    test_mode: bool = False
):
    """
    Ingest alert from proxy.
    On ingest, create DB Alert record, compute forensic bundle, return possible action.
    """
    # Convert proxy alert to event format for detector
    event = {
        "event_type": alert_data.heuristic,
        "timestamp": alert_data.timestamp,
        "size_bytes": alert_data.bytes,
        "session_id": alert_data.session_id
    }
    
    # Run detection engine
    detection_result = detection_engine.evaluate(event)
    
    # Determine if we should contain
    action = "no-op"
    if detection_result["is_alert"]:
        # Check if auto-contain is enabled
        if settings.AUTO_CONTAIN_ON_ALERT:
            action = "contain"
        # Or if severity is high
        elif detection_result["severity"] == "high":
            action = "contain"
    
    # Create alert record
    alert_id = f"ALERT_{int(time.time() * 1000)}"
    alert = Alert(
        alert_id=alert_id,
        session_id=alert_data.session_id,
        timestamp=datetime.fromtimestamp(alert_data.timestamp),
        event_type=alert_data.heuristic,
        event_data={
            "client_ip": alert_data.client_ip,
            "upstream_ip": alert_data.upstream_ip,
            "bytes": alert_data.bytes,
            "recent_samples": alert_data.recent_samples,
            "session_stats": alert_data.session_stats
        },
        detection_methods=detection_result["detection_methods"],
        severity=AlertSeverity[detection_result["severity"].upper()],
        ml_score=detection_result.get("ml_score"),
        rule_reasons=detection_result.get("reasons", []),
        status="open"
    )
    
    # Create forensic bundle
    artifacts = [
        {"hash": f"artifact_{i}", "type": "sample", "data": sample}
        for i, sample in enumerate(alert_data.recent_samples[-5:])  # Last 5 samples
    ]
    forensic_bundle = create_forensic_bundle(
        {"alert_id": alert_id},
        artifacts
    )
    
    alert.forensic_hash = forensic_bundle["merkle_root"]
    alert.blockchain_tx_hash = forensic_bundle.get("blockchain_tx_hash")
    
    db.add(alert)
    db.commit()
    db.refresh(alert)
    
    # Process alert asynchronously (or synchronously in local dev)
    process_alert_sync({"alert_id": alert_id})
    
    return {
        "action": action,
        "alert_id": alert_id,
        "severity": detection_result["severity"],
        "forensic_hash": forensic_bundle["merkle_root"],
        "blockchain_tx_hash": forensic_bundle.get("blockchain_tx_hash")
    }


@app.post("/api/v1/contain", response_model=ContainResponse)
async def contain_session(
    contain_request: ContainRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Admin endpoint to request/proxy a containment action on session id.
    In production, this would communicate with the proxy to actually contain the session.
    """
    # Find alerts for this session
    alerts = db.query(Alert).filter(Alert.session_id == contain_request.session_id).all()
    
    if not alerts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No alerts found for session {contain_request.session_id}"
        )
    
    # Mark alerts as contained
    for alert in alerts:
        alert.contained = True
        alert.contained_at = datetime.utcnow()
        alert.status = "contained"
    
    db.commit()
    
    # In production, here we would:
    # 1. Send containment command to proxy
    # 2. Log the action
    # 3. Send notifications
    
    return ContainResponse(
        success=True,
        session_id=contain_request.session_id,
        message=f"Session {contain_request.session_id} contained successfully"
    )


@app.get("/api/v1/alerts", response_model=list[AlertResponse])
async def list_alerts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List recent alerts"""
    alerts = db.query(Alert).order_by(Alert.timestamp.desc()).offset(skip).limit(limit).all()
    
    return [
        AlertResponse(
            id=a.id,
            alert_id=a.alert_id,
            session_id=a.session_id,
            timestamp=a.timestamp,
            event_type=a.event_type,
            event_data=a.event_data,
            detection_methods=a.detection_methods,
            severity=a.severity.value,
            ml_score=a.ml_score,
            rule_reasons=a.rule_reasons,
            status=a.status,
            contained=a.contained,
            forensic_hash=a.forensic_hash,
            blockchain_tx_hash=a.blockchain_tx_hash,
            created_at=a.created_at
        )
        for a in alerts
    ]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

