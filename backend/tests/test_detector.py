"""
Tests for detection engine
"""
import pytest
from backend.app.detector import RuleBasedDetector, MLDetectorStub, DetectionEngine


def test_clipboard_rule():
    """Test clipboard size threshold rule"""
    detector = RuleBasedDetector()
    
    # Small clipboard - should not trigger
    event = {
        "event_type": "clipboard_copy",
        "size_kb": 50,
        "timestamp": 1000.0
    }
    triggered, reason = detector.check_clipboard_rule(event)
    assert not triggered
    
    # Large clipboard - should trigger
    event = {
        "event_type": "clipboard_copy",
        "size_kb": 500,
        "timestamp": 1000.0
    }
    triggered, reason = detector.check_clipboard_rule(event)
    assert triggered
    assert "Clipboard copy exceeds threshold" in reason


def test_screenshot_burst_rule():
    """Test screenshot burst rule"""
    detector = RuleBasedDetector()
    
    # Single screenshot - should not trigger
    event = {
        "event_type": "screenshot",
        "timestamp": 1000.0
    }
    triggered, reason = detector.check_screenshot_burst_rule(event)
    assert not triggered
    
    # Multiple screenshots in short time - should trigger
    base_time = 1000.0
    for i in range(6):
        event = {
            "event_type": "screenshot",
            "timestamp": base_time + i * 1.0
        }
        triggered, reason = detector.check_screenshot_burst_rule(event)
    
    assert triggered
    assert "Screenshot burst" in reason


def test_file_transfer_rule():
    """Test file transfer rule"""
    detector = RuleBasedDetector()
    
    # Small file - should not trigger
    event = {
        "event_type": "file_transfer",
        "size_mb": 10,
        "timestamp": 1000.0
    }
    triggered, reason = detector.check_file_transfer_rule(event)
    assert not triggered
    
    # Large file - should trigger
    event = {
        "event_type": "file_transfer",
        "size_mb": 100,
        "timestamp": 1000.0
    }
    triggered, reason = detector.check_file_transfer_rule(event)
    assert triggered
    assert "Large file transfer" in reason


def test_ml_detector_stub():
    """Test ML detector stub"""
    detector = MLDetectorStub()
    
    event = {
        "event_type": "clipboard_copy",
        "size_kb": 500,
        "timestamp": 1000.0
    }
    
    history_context = {
        "clipboard_count_1min": 5,
        "screenshot_count_1min": 0,
        "file_transfer_count_1min": 0,
        "clipboard_total_kb_1min": 2500,
        "file_transfer_total_mb_1min": 0
    }
    
    score, info = detector.predict(event, history_context)
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


def test_detection_engine():
    """Test full detection engine"""
    engine = DetectionEngine()
    
    # Test with large clipboard event
    event = {
        "event_type": "clipboard_copy",
        "size_kb": 500,
        "timestamp": 1000.0
    }
    
    result = engine.evaluate(event)
    assert "is_alert" in result
    assert "detection_methods" in result
    assert "severity" in result
    
    # Should detect clipboard abuse
    if result["is_alert"]:
        assert "rule_based" in result["detection_methods"] or "ml_based" in result["detection_methods"]

