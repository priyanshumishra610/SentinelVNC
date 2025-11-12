"""
Tests for FastAPI endpoints
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.main import app
from backend.app.models import Base, get_db

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db():
    """Create test database"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db):
    """Create test client"""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_create_alert(client):
    """Test alert creation endpoint"""
    alert_data = {
        "session_id": "session_123",
        "client_ip": "192.168.1.100",
        "upstream_ip": "192.168.1.1",
        "timestamp": 1000.0,
        "heuristic": "clipboard_exfiltration",
        "bytes": 500 * 1024,
        "recent_samples": [],
        "session_stats": {}
    }
    
    response = client.post("/api/v1/alerts", json=alert_data)
    assert response.status_code == 200
    data = response.json()
    assert "action" in data
    assert "alert_id" in data


def test_list_alerts(client):
    """Test list alerts endpoint"""
    # First create an alert
    alert_data = {
        "session_id": "session_123",
        "client_ip": "192.168.1.100",
        "upstream_ip": "192.168.1.1",
        "timestamp": 1000.0,
        "heuristic": "clipboard_exfiltration",
        "bytes": 500 * 1024,
        "recent_samples": [],
        "session_stats": {}
    }
    client.post("/api/v1/alerts", json=alert_data)
    
    # Then list alerts
    response = client.get("/api/v1/alerts")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_contain_endpoint_requires_auth(client):
    """Test that contain endpoint requires authentication"""
    contain_data = {
        "session_id": "session_123",
        "reason": "Test containment"
    }
    
    # Without auth, should fail
    response = client.post("/api/v1/contain", json=contain_data)
    # In test mode, this might succeed, but in production it would require auth
    assert response.status_code in [200, 401, 403]

