"""
Pytest configuration and fixtures for SentinelVNC tests.
"""
import pytest
import tempfile
import shutil
from pathlib import Path
import json
import time


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_clipboard_event():
    """Sample clipboard copy event."""
    return {
        "event_type": "clipboard_copy",
        "timestamp": time.time(),
        "size_bytes": 300 * 1024,  # 300KB
        "size_kb": 300,
        "content_preview": "[300KB of data]",
        "source": "vnc_client"
    }


@pytest.fixture
def sample_screenshot_event():
    """Sample screenshot event."""
    return {
        "event_type": "screenshot",
        "timestamp": time.time(),
        "screenshot_path": "/tmp/screenshot.png",
        "resolution": "1920x1080",
        "source": "vnc_client"
    }


@pytest.fixture
def sample_file_transfer_event():
    """Sample file transfer event."""
    return {
        "event_type": "file_transfer",
        "timestamp": time.time(),
        "filename": "sensitive_data.zip",
        "size_bytes": 100 * 1024 * 1024,  # 100MB
        "size_mb": 100.0,
        "source": "vnc_client"
    }


@pytest.fixture
def sample_normal_clipboard_event():
    """Sample normal (non-anomalous) clipboard event."""
    return {
        "event_type": "clipboard_copy",
        "timestamp": time.time(),
        "size_bytes": 50 * 1024,  # 50KB
        "size_kb": 50,
        "content_preview": "[50KB of data]",
        "source": "vnc_client"
    }


@pytest.fixture
def events_file(temp_dir):
    """Create a temporary events file."""
    events_file = temp_dir / "vnc_events.jsonl"
    events_file.parent.mkdir(parents=True, exist_ok=True)
    return events_file


@pytest.fixture
def forensic_dir(temp_dir):
    """Create a temporary forensic directory."""
    forensic_dir = temp_dir / "forensic"
    forensic_dir.mkdir(parents=True, exist_ok=True)
    return forensic_dir


@pytest.fixture
def anchors_dir(temp_dir):
    """Create a temporary anchors directory."""
    anchors_dir = temp_dir / "anchors"
    anchors_dir.mkdir(parents=True, exist_ok=True)
    return anchors_dir


@pytest.fixture
def model_dir(temp_dir):
    """Create a temporary models directory."""
    model_dir = temp_dir / "models"
    model_dir.mkdir(parents=True, exist_ok=True)
    return model_dir


@pytest.fixture
def alerts_file(temp_dir):
    """Create a temporary alerts file."""
    alerts_file = temp_dir / "logs" / "alerts.jsonl"
    alerts_file.parent.mkdir(parents=True, exist_ok=True)
    return alerts_file



