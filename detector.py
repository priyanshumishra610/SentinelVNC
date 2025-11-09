#!/usr/bin/env python3
"""
SentinelVNC Detector
Hybrid rule-based + ML detection engine for VNC data exfiltration.
Generates alerts with explainable reasons and forensic JSON.
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import numpy as np
import pandas as pd
from collections import deque
import joblib


class RuleBasedDetector:
    """Rule-based detection engine with 3 core rules."""
    
    def __init__(self):
        self.clipboard_history = deque(maxlen=100)
        self.screenshot_history = deque(maxlen=100)
        self.file_transfer_history = deque(maxlen=100)
        
        # Rule thresholds
        self.CLIPBOARD_SIZE_THRESHOLD_KB = 200  # Alert if clipboard > 200KB
        self.SCREENSHOT_BURST_COUNT = 5  # Alert if 5+ screenshots in short time
        self.SCREENSHOT_BURST_WINDOW_SEC = 10  # Within 10 seconds
        self.FILE_TRANSFER_SIZE_THRESHOLD_MB = 50  # Alert if file > 50MB
        self.RAPID_FILE_TRANSFER_COUNT = 2  # Alert if 2+ large files in short time
        self.RAPID_FILE_TRANSFER_WINDOW_SEC = 30  # Within 30 seconds
    
    def check_clipboard_size_rule(self, event: Dict) -> Tuple[bool, str]:
        """Rule 1: Detect large clipboard operations."""
        if event.get("event_type") != "clipboard_copy":
            return False, ""
        
        size_kb = event.get("size_kb", 0)
        self.clipboard_history.append(event)
        
        if size_kb > self.CLIPBOARD_SIZE_THRESHOLD_KB:
            reason = f"Clipboard copy exceeds threshold: {size_kb}KB > {self.CLIPBOARD_SIZE_THRESHOLD_KB}KB"
            return True, reason
        
        return False, ""
    
    def check_screenshot_burst_rule(self, event: Dict) -> Tuple[bool, str]:
        """Rule 2: Detect screenshot scraping (burst pattern)."""
        if event.get("event_type") != "screenshot":
            return False, ""
        
        self.screenshot_history.append(event)
        current_time = event.get("timestamp", time.time())
        
        # Count screenshots in the burst window
        recent_screenshots = [
            e for e in self.screenshot_history
            if current_time - e.get("timestamp", 0) <= self.SCREENSHOT_BURST_WINDOW_SEC
        ]
        
        if len(recent_screenshots) >= self.SCREENSHOT_BURST_COUNT:
            reason = f"Screenshot burst detected: {len(recent_screenshots)} screenshots in {self.SCREENSHOT_BURST_WINDOW_SEC} seconds"
            return True, reason
        
        return False, ""
    
    def check_file_transfer_rule(self, event: Dict) -> Tuple[bool, str]:
        """Rule 3: Detect rapid large file transfers."""
        if event.get("event_type") != "file_transfer":
            return False, ""
        
        self.file_transfer_history.append(event)
        current_time = event.get("timestamp", time.time())
        size_mb = event.get("size_mb", 0)
        
        # Check single large file
        if size_mb > self.FILE_TRANSFER_SIZE_THRESHOLD_MB:
            reason = f"Large file transfer detected: {size_mb}MB > {self.FILE_TRANSFER_SIZE_THRESHOLD_MB}MB"
            return True, reason
        
        # Check rapid multiple transfers
        recent_transfers = [
            e for e in self.file_transfer_history
            if current_time - e.get("timestamp", 0) <= self.RAPID_FILE_TRANSFER_WINDOW_SEC
        ]
        
        if len(recent_transfers) >= self.RAPID_FILE_TRANSFER_COUNT:
            total_size = sum(e.get("size_mb", 0) for e in recent_transfers)
            reason = f"Rapid file transfer detected: {len(recent_transfers)} files ({total_size:.1f}MB total) in {self.RAPID_FILE_TRANSFER_WINDOW_SEC} seconds"
            return True, reason
        
        return False, ""
    
    def evaluate_rules(self, event: Dict) -> Tuple[bool, List[str]]:
        """Evaluate all rules and return (is_alert, reasons)."""
        reasons = []
        
        triggered, reason = self.check_clipboard_size_rule(event)
        if triggered:
            reasons.append(f"Rule 1: {reason}")
        
        triggered, reason = self.check_screenshot_burst_rule(event)
        if triggered:
            reasons.append(f"Rule 2: {reason}")
        
        triggered, reason = self.check_file_transfer_rule(event)
        if triggered:
            reasons.append(f"Rule 3: {reason}")
        
        return len(reasons) > 0, reasons


class MLDetector:
    """ML-based anomaly detection using trained model."""
    
    def __init__(self, model_path: str = "models/detection_model.pkl"):
        self.model_path = Path(model_path)
        self.model = None
        self.feature_names = None
        self.load_model()
    
    def load_model(self):
        """Load trained ML model."""
        if self.model_path.exists():
            try:
                model_data = joblib.load(self.model_path)
                self.model = model_data.get("model")
                self.feature_names = model_data.get("feature_names", [])
                print(f"[MLDetector] Loaded model from {self.model_path}")
            except Exception as e:
                print(f"[MLDetector] Warning: Could not load model: {e}")
                self.model = None
        else:
            print(f"[MLDetector] Warning: Model not found at {self.model_path}")
            self.model = None
    
    def extract_features(self, event: Dict, history_context: Dict) -> np.ndarray:
        """Extract features from event for ML model."""
        features = []
        
        # Event type encoding
        event_type = event.get("event_type", "unknown")
        features.append(1.0 if event_type == "clipboard_copy" else 0.0)
        features.append(1.0 if event_type == "screenshot" else 0.0)
        features.append(1.0 if event_type == "file_transfer" else 0.0)
        
        # Size features
        if event_type == "clipboard_copy":
            features.append(event.get("size_kb", 0) / 1000.0)  # Normalize to MB
            features.append(0.0)  # file size
        elif event_type == "file_transfer":
            features.append(0.0)  # clipboard size
            features.append(event.get("size_mb", 0))
        else:
            features.append(0.0)
            features.append(0.0)
        
        # Temporal features
        current_time = event.get("timestamp", time.time())
        features.append(current_time % 86400 / 86400.0)  # Time of day (normalized)
        
        # History-based features
        clipboard_count = history_context.get("clipboard_count_1min", 0)
        screenshot_count = history_context.get("screenshot_count_1min", 0)
        file_transfer_count = history_context.get("file_transfer_count_1min", 0)
        
        features.append(clipboard_count / 10.0)  # Normalize
        features.append(screenshot_count / 10.0)
        features.append(file_transfer_count / 10.0)
        
        # Rate features
        features.append(history_context.get("clipboard_total_kb_1min", 0) / 1000.0)
        features.append(history_context.get("file_transfer_total_mb_1min", 0))
        
        return np.array(features).reshape(1, -1)
    
    def predict(self, event: Dict, history_context: Dict) -> Tuple[float, Dict]:
        """Predict anomaly score and return explainability info."""
        if self.model is None:
            return 0.0, {"error": "Model not loaded"}
        
        try:
            features = self.extract_features(event, history_context)
            score = self.model.predict_proba(features)[0][1]  # Probability of anomaly
            
            # Feature importance (simplified - in production use SHAP)
            feature_importance = {}
            if hasattr(self.model, 'feature_importances_'):
                importances = self.model.feature_importances_
                feature_names = self.feature_names or [f"feature_{i}" for i in range(len(importances))]
                for name, imp in zip(feature_names, importances):
                    feature_importance[name] = float(imp)
            
            return float(score), {
                "anomaly_score": float(score),
                "feature_importance": feature_importance,
                "threshold": 0.5
            }
        except Exception as e:
            print(f"[MLDetector] Prediction error: {e}")
            return 0.0, {"error": str(e)}


class HybridDetector:
    """Combines rule-based and ML detection."""
    
    def __init__(self, events_file: str = "data/synthetic/vnc_events.jsonl",
                 model_path: str = "models/detection_model.pkl"):
        self.rule_detector = RuleBasedDetector()
        self.ml_detector = MLDetector(model_path)
        self.events_file = Path(events_file)
        self.alerts_file = Path("logs/alerts.jsonl")
        self.forensic_dir = Path("forensic")
        self.forensic_dir.mkdir(parents=True, exist_ok=True)
        self.alerts_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Track processed events
        self.processed_lines = set()
        self.history_window = deque(maxlen=1000)  # Last 1000 events for context
    
    def get_history_context(self, current_time: float) -> Dict:
        """Get historical context for ML features."""
        one_minute_ago = current_time - 60
        
        recent_events = [
            e for e in self.history_window
            if e.get("timestamp", 0) >= one_minute_ago
        ]
        
        context = {
            "clipboard_count_1min": sum(1 for e in recent_events if e.get("event_type") == "clipboard_copy"),
            "screenshot_count_1min": sum(1 for e in recent_events if e.get("event_type") == "screenshot"),
            "file_transfer_count_1min": sum(1 for e in recent_events if e.get("event_type") == "file_transfer"),
            "clipboard_total_kb_1min": sum(e.get("size_kb", 0) for e in recent_events if e.get("event_type") == "clipboard_copy"),
            "file_transfer_total_mb_1min": sum(e.get("size_mb", 0) for e in recent_events if e.get("event_type") == "file_transfer"),
        }
        
        return context
    
    def process_event(self, event: Dict) -> Optional[Dict]:
        """Process a single event and generate alert if needed."""
        # Update history
        self.history_window.append(event)
        
        # Rule-based detection
        rule_alert, rule_reasons = self.rule_detector.evaluate_rules(event)
        
        # ML-based detection
        history_context = self.get_history_context(event.get("timestamp", time.time()))
        ml_score, ml_info = self.ml_detector.predict(event, history_context)
        ml_alert = ml_score > 0.5  # Threshold
        
        # Combine results
        is_alert = rule_alert or ml_alert
        if not is_alert:
            return None
        
        # Generate alert
        alert = {
            "alert_id": f"ALERT_{int(time.time() * 1000)}",
            "timestamp": event.get("timestamp", time.time()),
            "event": event,
            "detection_methods": [],
            "reasons": [],
            "severity": "high" if rule_alert and ml_alert else "medium",
            "ml_score": ml_score,
            "ml_info": ml_info
        }
        
        if rule_alert:
            alert["detection_methods"].append("rule_based")
            alert["reasons"].extend(rule_reasons)
        
        if ml_alert:
            alert["detection_methods"].append("ml_based")
            alert["reasons"].append(f"ML anomaly score: {ml_score:.3f} (threshold: 0.5)")
        
        return alert
    
    def generate_forensic_json(self, alert: Dict) -> Dict:
        """Generate forensic JSON anchor for blockchain."""
        forensic = {
            "forensic_id": alert["alert_id"],
            "timestamp": alert["timestamp"],
            "datetime": datetime.fromtimestamp(alert["timestamp"]).isoformat(),
            "event_type": alert["event"].get("event_type"),
            "detection_methods": alert["detection_methods"],
            "reasons": alert["reasons"],
            "severity": alert["severity"],
            "ml_score": alert["ml_score"],
            "event_details": alert["event"],
            "containment_status": "pending",
            "hash": self._compute_hash(alert)
        }
        
        # Save forensic JSON
        forensic_file = self.forensic_dir / f"{alert['alert_id']}.json"
        with open(forensic_file, 'w') as f:
            json.dump(forensic, f, indent=2)
        
        return forensic
    
    def _compute_hash(self, alert: Dict) -> str:
        """Compute hash of alert for integrity verification."""
        import hashlib
        alert_str = json.dumps(alert, sort_keys=True)
        return hashlib.sha256(alert_str.encode()).hexdigest()
    
    def poll_events(self, continuous: bool = False):
        """Poll events file and process new events."""
        if not self.events_file.exists():
            print(f"[Detector] Events file not found: {self.events_file}")
            return
        
        while True:
            try:
                with open(self.events_file, 'r') as f:
                    lines = f.readlines()
                
                new_events = []
                for i, line in enumerate(lines):
                    if i not in self.processed_lines:
                        try:
                            event = json.loads(line.strip())
                            new_events.append((i, event))
                            self.processed_lines.add(i)
                        except json.JSONDecodeError:
                            continue
                
                # Process new events
                for line_num, event in new_events:
                    alert = self.process_event(event)
                    if alert:
                        # Save alert
                        with open(self.alerts_file, 'a') as f:
                            f.write(json.dumps(alert) + '\n')
                        
                        # Generate forensic JSON
                        forensic = self.generate_forensic_json(alert)
                        
                        print(f"[Detector] ALERT: {alert['alert_id']}")
                        print(f"  Reasons: {', '.join(alert['reasons'])}")
                        print(f"  Severity: {alert['severity']}")
                        print(f"  Forensic: {forensic['forensic_id']}.json")
                
                if not continuous:
                    break
                
                time.sleep(1)  # Poll every second
                
            except KeyboardInterrupt:
                print("\n[Detector] Stopped by user")
                break
            except Exception as e:
                print(f"[Detector] Error: {e}")
                time.sleep(1)


if __name__ == "__main__":
    # Test the detector
    detector = HybridDetector()
    print("Polling for events...")
    detector.poll_events(continuous=False)
    print("Done.")

