"""
Integration tests for SentinelVNC end-to-end workflows.
"""
import pytest
import json
import time
import joblib
from pathlib import Path
from attack_simulator import AttackSimulator
from detector import HybridDetector
from merkle_anchor import ForensicAnchoring
from train_model import train_model
import numpy as np
from sklearn.ensemble import RandomForestClassifier


class TestEndToEndWorkflow:
    """Test complete end-to-end workflows."""
    
    def test_full_detection_workflow(self, temp_dir):
        """Test complete detection workflow: simulate -> detect -> anchor."""
        # Setup directories
        data_dir = temp_dir / "data" / "synthetic"
        models_dir = temp_dir / "models"
        logs_dir = temp_dir / "logs"
        forensic_dir = temp_dir / "forensic"
        anchors_dir = temp_dir / "anchors"
        
        for d in [data_dir, models_dir, logs_dir, forensic_dir, anchors_dir]:
            d.mkdir(parents=True, exist_ok=True)
        
        # Step 1: Create a simple model
        model_path = models_dir / "detection_model.pkl"
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        X_dummy = np.random.rand(100, 11)
        y_dummy = np.random.randint(0, 2, 100)
        model.fit(X_dummy, y_dummy)
        
        model_data = {
            "model": model,
            "feature_names": [f"feature_{i}" for i in range(11)]
        }
        joblib.dump(model_data, model_path)
        
        # Step 2: Simulate attacks
        sim = AttackSimulator(output_dir=str(data_dir))
        events = sim.simulate_clipboard_abuse(burst_size=3, size_kb=300)
        sim.save_events(events)
        
        # Step 3: Run detector
        detector = HybridDetector(
            events_file=str(sim.events_file),
            model_path=str(model_path)
        )
        detector.alerts_file = logs_dir / "alerts.jsonl"
        detector.forensic_dir = forensic_dir
        
        detector.poll_events(continuous=False)
        
        # Step 4: Verify alerts were created
        assert detector.alerts_file.exists()
        with open(detector.alerts_file, 'r') as f:
            alerts = [json.loads(line) for line in f if line.strip()]
        
        assert len(alerts) > 0
        
        # Step 5: Verify forensic files were created
        forensic_files = list(forensic_dir.glob("*.json"))
        assert len(forensic_files) == len(alerts)
        
        # Step 6: Create anchor
        anchorer = ForensicAnchoring(
            forensic_dir=str(forensic_dir),
            anchors_dir=str(anchors_dir)
        )
        anchor = anchorer.create_anchor()
        
        assert anchor != {}
        assert "merkle_root" in anchor
        assert anchor["forensic_count"] == len(forensic_files)
        
        # Step 7: Verify anchor
        anchor_file = anchors_dir / f"{anchor['anchor_id']}.json"
        assert anchorer.verify_anchor(anchor_file) is True
    
    def test_detection_with_multiple_event_types(self, temp_dir):
        """Test detection with multiple event types."""
        # Setup
        data_dir = temp_dir / "data" / "synthetic"
        models_dir = temp_dir / "models"
        logs_dir = temp_dir / "logs"
        forensic_dir = temp_dir / "forensic"
        
        for d in [data_dir, models_dir, logs_dir, forensic_dir]:
            d.mkdir(parents=True, exist_ok=True)
        
        # Create model
        model_path = models_dir / "detection_model.pkl"
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        X_dummy = np.random.rand(100, 11)
        y_dummy = np.random.randint(0, 2, 100)
        model.fit(X_dummy, y_dummy)
        
        model_data = {
            "model": model,
            "feature_names": [f"feature_{i}" for i in range(11)]
        }
        joblib.dump(model_data, model_path)
        
        # Simulate mixed attacks
        sim = AttackSimulator(output_dir=str(data_dir))
        events = []
        events.extend(sim.simulate_clipboard_abuse(burst_size=2, size_kb=250))
        events.extend(sim.simulate_screenshot_scraping(count=6, interval_seconds=1.0))
        events.extend(sim.simulate_file_exfiltration(file_count=2, size_mb=60.0))
        sim.save_events(events)
        
        # Run detector
        detector = HybridDetector(
            events_file=str(sim.events_file),
            model_path=str(model_path)
        )
        detector.alerts_file = logs_dir / "alerts.jsonl"
        detector.forensic_dir = forensic_dir
        
        detector.poll_events(continuous=False)
        
        # Verify alerts
        assert detector.alerts_file.exists()
        with open(detector.alerts_file, 'r') as f:
            alerts = [json.loads(line) for line in f if line.strip()]
        
        assert len(alerts) > 0
        
        # Check that different event types triggered alerts
        event_types = [alert["event"]["event_type"] for alert in alerts]
        assert "clipboard_copy" in event_types or "screenshot" in event_types or "file_transfer" in event_types
    
    def test_rule_based_detection_only(self, temp_dir):
        """Test detection works even without ML model."""
        # Setup
        data_dir = temp_dir / "data" / "synthetic"
        logs_dir = temp_dir / "logs"
        forensic_dir = temp_dir / "forensic"
        
        for d in [data_dir, logs_dir, forensic_dir]:
            d.mkdir(parents=True, exist_ok=True)
        
        # Simulate attacks
        sim = AttackSimulator(output_dir=str(data_dir))
        events = sim.simulate_clipboard_abuse(burst_size=2, size_kb=300)
        sim.save_events(events)
        
        # Run detector without model
        detector = HybridDetector(
            events_file=str(sim.events_file),
            model_path=str(temp_dir / "nonexistent_model.pkl")
        )
        detector.alerts_file = logs_dir / "alerts.jsonl"
        detector.forensic_dir = forensic_dir
        
        detector.poll_events(continuous=False)
        
        # Should still detect via rules
        assert detector.alerts_file.exists()
        with open(detector.alerts_file, 'r') as f:
            alerts = [json.loads(line) for line in f if line.strip()]
        
        assert len(alerts) > 0
        # Should have rule-based detection
        assert any("rule_based" in alert["detection_methods"] for alert in alerts)
    
    def test_anchor_verification_after_tampering(self, temp_dir):
        """Test anchor verification detects tampering."""
        # Setup
        forensic_dir = temp_dir / "forensic"
        anchors_dir = temp_dir / "anchors"
        
        for d in [forensic_dir, anchors_dir]:
            d.mkdir(parents=True, exist_ok=True)
        
        # Create forensic files
        for i in range(3):
            forensic_file = forensic_dir / f"forensic_{i}.json"
            data = {
                "forensic_id": f"FORENSIC_{i}",
                "timestamp": time.time() + i,
                "event_type": "clipboard_copy"
            }
            with open(forensic_file, 'w') as f:
                json.dump(data, f)
        
        # Create anchor
        anchorer = ForensicAnchoring(
            forensic_dir=str(forensic_dir),
            anchors_dir=str(anchors_dir)
        )
        anchor = anchorer.create_anchor()
        anchor_file = anchors_dir / f"{anchor['anchor_id']}.json"
        
        # Verify anchor is valid
        assert anchorer.verify_anchor(anchor_file) is True
        
        # Tamper with forensic file
        forensic_file = forensic_dir / "forensic_0.json"
        with open(forensic_file, 'w') as f:
            json.dump({"forensic_id": "TAMPERED", "timestamp": time.time()}, f)
        
        # Verify anchor is now invalid
        assert anchorer.verify_anchor(anchor_file) is False




