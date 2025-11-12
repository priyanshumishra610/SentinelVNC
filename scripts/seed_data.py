#!/usr/bin/env python3
"""
Seed data script - create sample models/users and sample alerts
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from backend.app.models import Base, engine, SessionLocal, User, Alert, AlertSeverity
from backend.app.config import settings
from datetime import datetime, timedelta
import time
import hashlib


def create_sample_users(db: Session):
    """Create sample users"""
    users = [
        {
            "username": "admin",
            "email": "admin@sentinelvnc.local",
            "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5",  # password: admin
            "is_admin": True
        },
        {
            "username": "analyst",
            "email": "analyst@sentinelvnc.local",
            "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5",  # password: analyst
            "is_admin": False
        }
    ]
    
    for user_data in users:
        existing = db.query(User).filter(User.username == user_data["username"]).first()
        if not existing:
            user = User(**user_data)
            db.add(user)
            print(f"Created user: {user_data['username']}")
    
    db.commit()


def create_sample_alerts(db: Session):
    """Create sample alerts"""
    alerts = [
        {
            "alert_id": f"ALERT_{int(time.time() * 1000)}",
            "session_id": "session_001",
            "timestamp": datetime.utcnow() - timedelta(hours=1),
            "event_type": "clipboard_exfiltration",
            "event_data": {
                "client_ip": "192.168.1.100",
                "upstream_ip": "192.168.1.1",
                "bytes": 500 * 1024,
                "heuristic": "clipboard_exfiltration"
            },
            "detection_methods": ["rule_based", "ml_based"],
            "severity": AlertSeverity.HIGH,
            "ml_score": 0.85,
            "rule_reasons": ["Rule 1: Clipboard copy exceeds threshold: 500KB > 200KB"],
            "status": "open",
            "forensic_hash": hashlib.sha256(b"sample_forensic_1").hexdigest(),
            "blockchain_tx_hash": hashlib.sha256(b"sample_tx_1").hexdigest()[:66]
        },
        {
            "alert_id": f"ALERT_{int(time.time() * 1000) + 1}",
            "session_id": "session_002",
            "timestamp": datetime.utcnow() - timedelta(minutes=30),
            "event_type": "screenshot_burst",
            "event_data": {
                "client_ip": "192.168.1.101",
                "upstream_ip": "192.168.1.1",
                "bytes": 0,
                "heuristic": "screenshot_burst"
            },
            "detection_methods": ["rule_based"],
            "severity": AlertSeverity.MEDIUM,
            "ml_score": 0.45,
            "rule_reasons": ["Rule 2: Screenshot burst: 6 screenshots in 10s"],
            "status": "open",
            "forensic_hash": hashlib.sha256(b"sample_forensic_2").hexdigest(),
            "blockchain_tx_hash": hashlib.sha256(b"sample_tx_2").hexdigest()[:66]
        },
        {
            "alert_id": f"ALERT_{int(time.time() * 1000) + 2}",
            "session_id": "session_003",
            "timestamp": datetime.utcnow() - timedelta(minutes=15),
            "event_type": "file_transfer_like",
            "event_data": {
                "client_ip": "192.168.1.102",
                "upstream_ip": "192.168.1.1",
                "bytes": 100 * 1024 * 1024,
                "heuristic": "file_transfer_like"
            },
            "detection_methods": ["rule_based", "ml_based"],
            "severity": AlertSeverity.HIGH,
            "ml_score": 0.92,
            "rule_reasons": ["Rule 3: Large file transfer: 100MB > 50MB"],
            "status": "contained",
            "contained": True,
            "contained_at": datetime.utcnow() - timedelta(minutes=10),
            "forensic_hash": hashlib.sha256(b"sample_forensic_3").hexdigest(),
            "blockchain_tx_hash": hashlib.sha256(b"sample_tx_3").hexdigest()[:66]
        }
    ]
    
    for alert_data in alerts:
        existing = db.query(Alert).filter(Alert.alert_id == alert_data["alert_id"]).first()
        if not existing:
            alert = Alert(**alert_data)
            db.add(alert)
            print(f"Created alert: {alert_data['alert_id']}")
    
    db.commit()


def create_sample_ml_model():
    """Create a sample ML model for testing"""
    from sklearn.ensemble import RandomForestClassifier
    import joblib
    import numpy as np
    
    model_path = Path("models/detection_model.pkl")
    model_path.parent.mkdir(parents=True, exist_ok=True)
    
    if model_path.exists():
        print(f"ML model already exists at {model_path}")
        return
    
    # Create a simple RandomForest model
    # Generate synthetic training data
    np.random.seed(42)
    X = np.random.rand(100, 10)
    y = (X.sum(axis=1) > 5).astype(int)
    
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X, y)
    
    # Save model
    model_data = {
        "model": model,
        "feature_names": [f"feature_{i}" for i in range(10)]
    }
    joblib.dump(model_data, model_path)
    print(f"Created sample ML model at {model_path}")


def main():
    """Main seed function"""
    print("Seeding database...")
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        create_sample_users(db)
        create_sample_alerts(db)
        print("Database seeded successfully!")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()
    
    # Create sample ML model
    print("\nCreating sample ML model...")
    create_sample_ml_model()
    print("Done!")


if __name__ == "__main__":
    main()

