"""
Unit tests for detector.py
"""
import pytest
import json
import time
import joblib
from pathlib import Path
from detector import RuleBasedDetector, MLDetector, HybridDetector
from sklearn.ensemble import RandomForestClassifier
import numpy as np


class TestRuleBasedDetector:
    """Test RuleBasedDetector class."""
    
    def test_init(self):
        """Test RuleBasedDetector initialization."""
        detector = RuleBasedDetector()
        assert detector.CLIPBOARD_SIZE_THRESHOLD_KB == 200
        assert detector.SCREENSHOT_BURST_COUNT == 5
        assert detector.SCREENSHOT_BURST_WINDOW_SEC == 10
        assert detector.FILE_TRANSFER_SIZE_THRESHOLD_MB == 50
    
    def test_check_clipboard_size_rule_triggered(self, sample_clipboard_event):
        """Test clipboard size rule triggers on large clipboard."""
        detector = RuleBasedDetector()
        # Modify event to be large
        sample_clipboard_event["size_kb"] = 300
        triggered, reason = detector.check_clipboard_size_rule(sample_clipboard_event)
        
        assert triggered is True
        assert "300KB" in reason
        assert "200KB" in reason
    
    def test_check_clipboard_size_rule_not_triggered(self, sample_normal_clipboard_event):
        """Test clipboard size rule doesn't trigger on normal clipboard."""
        detector = RuleBasedDetector()
        triggered, reason = detector.check_clipboard_size_rule(sample_normal_clipboard_event)
        
        assert triggered is False
        assert reason == ""
    
    def test_check_clipboard_size_rule_wrong_event_type(self, sample_screenshot_event):
        """Test clipboard rule doesn't trigger on non-clipboard events."""
        detector = RuleBasedDetector()
        triggered, reason = detector.check_clipboard_size_rule(sample_screenshot_event)
        
        assert triggered is False
    
    def test_check_screenshot_burst_rule_triggered(self):
        """Test screenshot burst rule triggers on rapid screenshots."""
        detector = RuleBasedDetector()
        base_time = time.time()
        
        # Generate 6 screenshots within 10 seconds
        for i in range(6):
            event = {
                "event_type": "screenshot",
                "timestamp": base_time + i * 1.0
            }
            triggered, reason = detector.check_screenshot_burst_rule(event)
        
        # Last one should trigger
        assert triggered is True
        assert "screenshot" in reason.lower()
    
    def test_check_screenshot_burst_rule_not_triggered(self):
        """Test screenshot burst rule doesn't trigger on slow screenshots."""
        detector = RuleBasedDetector()
        base_time = time.time()
        
        # Generate 3 screenshots with large intervals
        for i in range(3):
            event = {
                "event_type": "screenshot",
                "timestamp": base_time + i * 15.0  # 15 seconds apart
            }
            triggered, reason = detector.check_screenshot_burst_rule(event)
        
        assert triggered is False
    
    def test_check_file_transfer_rule_large_file(self, sample_file_transfer_event):
        """Test file transfer rule triggers on large file."""
        detector = RuleBasedDetector()
        sample_file_transfer_event["size_mb"] = 100.0  # 100MB > 50MB threshold
        triggered, reason = detector.check_file_transfer_rule(sample_file_transfer_event)
        
        assert triggered is True
        assert "100" in reason
        assert "50" in reason
    
    def test_check_file_transfer_rule_rapid_transfers(self):
        """Test file transfer rule triggers on rapid transfers."""
        detector = RuleBasedDetector()
        base_time = time.time()
        
        # Generate 2 file transfers within 30 seconds
        for i in range(2):
            event = {
                "event_type": "file_transfer",
                "timestamp": base_time + i * 5.0,
                "size_mb": 30.0  # Each file is 30MB (below single file threshold)
            }
            triggered, reason = detector.check_file_transfer_rule(event)
        
        # Second one should trigger
        assert triggered is True
        assert "rapid" in reason.lower() or "2" in reason
    
    def test_evaluate_rules_multiple_triggers(self):
        """Test evaluate_rules with multiple rule triggers."""
        detector = RuleBasedDetector()
        event = {
            "event_type": "clipboard_copy",
            "timestamp": time.time(),
            "size_kb": 300  # Triggers rule 1
        }
        is_alert, reasons = detector.evaluate_rules(event)
        
        assert is_alert is True
        assert len(reasons) > 0
        assert any("Rule 1" in r for r in reasons)


class TestMLDetector:
    """Test MLDetector class."""
    
    def test_init_no_model(self, temp_dir):
        """Test MLDetector initialization without model file."""
        model_path = temp_dir / "models" / "detection_model.pkl"
        detector = MLDetector(model_path=str(model_path))
        
        assert detector.model is None
    
    def test_init_with_model(self, temp_dir, model_dir):
        """Test MLDetector initialization with model file."""
        model_path = model_dir / "detection_model.pkl"
        
        # Create a dummy model
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        X_dummy = np.random.rand(100, 11)  # 11 features
        y_dummy = np.random.randint(0, 2, 100)
        model.fit(X_dummy, y_dummy)
        
        model_data = {
            "model": model,
            "feature_names": [f"feature_{i}" for i in range(11)]
        }
        joblib.dump(model_data, model_path)
        
        detector = MLDetector(model_path=str(model_path))
        assert detector.model is not None
        assert len(detector.feature_names) == 11
    
    def test_extract_features_clipboard(self):
        """Test feature extraction for clipboard event."""
        detector = MLDetector()
        event = {
            "event_type": "clipboard_copy",
            "size_kb": 250,
            "timestamp": time.time()
        }
        history_context = {
            "clipboard_count_1min": 5,
            "screenshot_count_1min": 2,
            "file_transfer_count_1min": 0,
            "clipboard_total_kb_1min": 500,
            "file_transfer_total_mb_1min": 0
        }
        
        features = detector.extract_features(event, history_context)
        
        assert features.shape == (1, 11)
        assert features[0][0] == 1.0  # is_clipboard
        assert features[0][1] == 0.0  # is_screenshot
        assert features[0][2] == 0.0  # is_file_transfer
    
    def test_predict_no_model(self):
        """Test predict when model is not loaded."""
        detector = MLDetector()
        event = {"event_type": "clipboard_copy"}
        history_context = {}
        
        score, info = detector.predict(event, history_context)
        
        assert score == 0.0
        assert "error" in info
    
    def test_predict_with_model(self, model_dir):
        """Test predict with loaded model."""
        model_path = model_dir / "detection_model.pkl"
        
        # Create and save model
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        X_dummy = np.random.rand(100, 11)
        y_dummy = np.random.randint(0, 2, 100)
        model.fit(X_dummy, y_dummy)
        
        model_data = {
            "model": model,
            "feature_names": [f"feature_{i}" for i in range(11)]
        }
        joblib.dump(model_data, model_path)
        
        detector = MLDetector(model_path=str(model_path))
        event = {
            "event_type": "clipboard_copy",
            "size_kb": 250,
            "timestamp": time.time()
        }
        history_context = {
            "clipboard_count_1min": 5,
            "screenshot_count_1min": 2,
            "file_transfer_count_1min": 0,
            "clipboard_total_kb_1min": 500,
            "file_transfer_total_mb_1min": 0
        }
        
        score, info = detector.predict(event, history_context)
        
        assert 0.0 <= score <= 1.0
        assert "anomaly_score" in info or "error" in info


class TestHybridDetector:
    """Test HybridDetector class."""
    
    def test_init(self, temp_dir):
        """Test HybridDetector initialization."""
        events_file = temp_dir / "events.jsonl"
        detector = HybridDetector(
            events_file=str(events_file),
            model_path=str(temp_dir / "models" / "detection_model.pkl")
        )
        
        assert detector.rule_detector is not None
        assert detector.ml_detector is not None
        assert detector.events_file == events_file
    
    def test_get_history_context(self, temp_dir):
        """Test history context generation."""
        detector = HybridDetector(
            events_file=str(temp_dir / "events.jsonl"),
            model_path=str(temp_dir / "models" / "detection_model.pkl")
        )
        
        current_time = time.time()
        # Add some events to history
        for i in range(5):
            event = {
                "event_type": "clipboard_copy",
                "timestamp": current_time - 30 + i * 5,  # Within last minute
                "size_kb": 50
            }
            detector.history_window.append(event)
        
        context = detector.get_history_context(current_time)
        
        assert "clipboard_count_1min" in context
        assert context["clipboard_count_1min"] == 5
    
    def test_process_event_rule_alert(self, temp_dir):
        """Test process_event with rule-based alert."""
        detector = HybridDetector(
            events_file=str(temp_dir / "events.jsonl"),
            model_path=str(temp_dir / "models" / "detection_model.pkl")
        )
        
        event = {
            "event_type": "clipboard_copy",
            "timestamp": time.time(),
            "size_kb": 300  # Triggers rule
        }
        
        alert = detector.process_event(event)
        
        assert alert is not None
        assert "alert_id" in alert
        assert "rule_based" in alert["detection_methods"]
        assert len(alert["reasons"]) > 0
    
    def test_process_event_no_alert(self, temp_dir):
        """Test process_event with no alert."""
        detector = HybridDetector(
            events_file=str(temp_dir / "events.jsonl"),
            model_path=str(temp_dir / "models" / "detection_model.pkl")
        )
        
        event = {
            "event_type": "clipboard_copy",
            "timestamp": time.time(),
            "size_kb": 50  # Normal size
        }
        
        alert = detector.process_event(event)
        
        assert alert is None
    
    def test_generate_forensic_json(self, temp_dir, forensic_dir):
        """Test forensic JSON generation."""
        detector = HybridDetector(
            events_file=str(temp_dir / "events.jsonl"),
            model_path=str(temp_dir / "models" / "detection_model.pkl")
        )
        detector.forensic_dir = forensic_dir
        
        alert = {
            "alert_id": "ALERT_123",
            "timestamp": time.time(),
            "event": {"event_type": "clipboard_copy"},
            "detection_methods": ["rule_based"],
            "reasons": ["Rule 1: Large clipboard"],
            "severity": "high",
            "ml_score": 0.0,
            "ml_info": {}
        }
        
        forensic = detector.generate_forensic_json(alert)
        
        assert forensic["forensic_id"] == "ALERT_123"
        assert "hash" in forensic
        forensic_file = forensic_dir / "ALERT_123.json"
        assert forensic_file.exists()
        
        # Verify file content
        with open(forensic_file, 'r') as f:
            saved_forensic = json.load(f)
            assert saved_forensic["forensic_id"] == "ALERT_123"
    
    def test_poll_events_file_not_exists(self, temp_dir):
        """Test poll_events when file doesn't exist."""
        detector = HybridDetector(
            events_file=str(temp_dir / "nonexistent.jsonl"),
            model_path=str(temp_dir / "models" / "detection_model.pkl")
        )
        
        # Should not raise error, just return
        detector.poll_events(continuous=False)
    
    def test_poll_events_processes_new_events(self, temp_dir, events_file):
        """Test poll_events processes new events."""
        detector = HybridDetector(
            events_file=str(events_file),
            model_path=str(temp_dir / "models" / "detection_model.pkl")
        )
        detector.alerts_file = temp_dir / "logs" / "alerts.jsonl"
        detector.alerts_file.parent.mkdir(parents=True, exist_ok=True)
        detector.forensic_dir = temp_dir / "forensic"
        detector.forensic_dir.mkdir(parents=True, exist_ok=True)
        
        # Write events to file
        with open(events_file, 'w') as f:
            event1 = {
                "event_type": "clipboard_copy",
                "timestamp": time.time(),
                "size_kb": 300  # Triggers alert
            }
            f.write(json.dumps(event1) + '\n')
        
        detector.poll_events(continuous=False)
        
        # Check alert was created
        if detector.alerts_file.exists():
            with open(detector.alerts_file, 'r') as f:
                alerts = [json.loads(line) for line in f]
                assert len(alerts) > 0

