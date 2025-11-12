"""
Detection engine glue - rule checks + ML stub
"""
import time
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import numpy as np
from collections import deque
import joblib
from backend.app.config import settings


class RuleBasedDetector:
    """Rule-based detection with configurable thresholds"""
    
    def __init__(self):
        self.clipboard_threshold_kb = 200
        self.screenshot_burst_count = 5
        self.screenshot_burst_window_sec = 10
        self.file_transfer_size_mb = 50
        self.rapid_file_transfer_count = 2
        self.rapid_file_transfer_window_sec = 30
        
        self.clipboard_history = deque(maxlen=100)
        self.screenshot_history = deque(maxlen=100)
        self.file_transfer_history = deque(maxlen=100)
    
    def check_clipboard_rule(self, event: Dict) -> Tuple[bool, str]:
        """Check clipboard size threshold"""
        if event.get("event_type") != "clipboard_copy":
            return False, ""
        
        size_kb = event.get("size_kb", 0)
        self.clipboard_history.append(event)
        
        if size_kb > self.clipboard_threshold_kb:
            return True, f"Clipboard copy exceeds threshold: {size_kb}KB > {self.clipboard_threshold_kb}KB"
        
        return False, ""
    
    def check_screenshot_burst_rule(self, event: Dict) -> Tuple[bool, str]:
        """Check screenshot burst pattern"""
        if event.get("event_type") != "screenshot":
            return False, ""
        
        self.screenshot_history.append(event)
        current_time = event.get("timestamp", time.time())
        
        recent_screenshots = [
            e for e in self.screenshot_history
            if current_time - e.get("timestamp", 0) <= self.screenshot_burst_window_sec
        ]
        
        if len(recent_screenshots) >= self.screenshot_burst_count:
            return True, f"Screenshot burst: {len(recent_screenshots)} screenshots in {self.screenshot_burst_window_sec}s"
        
        return False, ""
    
    def check_file_transfer_rule(self, event: Dict) -> Tuple[bool, str]:
        """Check file transfer patterns"""
        if event.get("event_type") != "file_transfer":
            return False, ""
        
        self.file_transfer_history.append(event)
        current_time = event.get("timestamp", time.time())
        size_mb = event.get("size_mb", 0)
        
        if size_mb > self.file_transfer_size_mb:
            return True, f"Large file transfer: {size_mb}MB > {self.file_transfer_size_mb}MB"
        
        recent_transfers = [
            e for e in self.file_transfer_history
            if current_time - e.get("timestamp", 0) <= self.rapid_file_transfer_window_sec
        ]
        
        if len(recent_transfers) >= self.rapid_file_transfer_count:
            total_size = sum(e.get("size_mb", 0) for e in recent_transfers)
            return True, f"Rapid file transfers: {len(recent_transfers)} files ({total_size:.1f}MB) in {self.rapid_file_transfer_window_sec}s"
        
        return False, ""
    
    def evaluate(self, event: Dict) -> Tuple[bool, List[str]]:
        """Evaluate all rules"""
        reasons = []
        
        triggered, reason = self.check_clipboard_rule(event)
        if triggered:
            reasons.append(f"Rule 1: {reason}")
        
        triggered, reason = self.check_screenshot_burst_rule(event)
        if triggered:
            reasons.append(f"Rule 2: {reason}")
        
        triggered, reason = self.check_file_transfer_rule(event)
        if triggered:
            reasons.append(f"Rule 3: {reason}")
        
        return len(reasons) > 0, reasons


class MLDetectorStub:
    """ML detector stub using RandomForestClassifier"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = Path(model_path or settings.ML_MODEL_PATH)
        self.model = None
        self.feature_names = None
        self.load_model()
    
    def load_model(self):
        """Load trained ML model"""
        if self.model_path.exists():
            try:
                model_data = joblib.load(self.model_path)
                self.model = model_data.get("model")
                self.feature_names = model_data.get("feature_names", [])
            except Exception as e:
                print(f"[MLDetector] Warning: Could not load model: {e}")
                self.model = None
        else:
            print(f"[MLDetector] Model not found, using stub")
            self.model = None
    
    def extract_features(self, event: Dict, history_context: Dict) -> np.ndarray:
        """Extract features from event"""
        features = []
        
        # Event type encoding
        event_type = event.get("event_type", "unknown")
        features.append(1.0 if event_type == "clipboard_copy" else 0.0)
        features.append(1.0 if event_type == "screenshot" else 0.0)
        features.append(1.0 if event_type == "file_transfer" else 0.0)
        
        # Size features
        if event_type == "clipboard_copy":
            features.append(event.get("size_kb", 0) / 1000.0)
            features.append(0.0)
        elif event_type == "file_transfer":
            features.append(0.0)
            features.append(event.get("size_mb", 0))
        else:
            features.append(0.0)
            features.append(0.0)
        
        # Temporal features
        current_time = event.get("timestamp", time.time())
        features.append(current_time % 86400 / 86400.0)
        
        # History features
        features.append(history_context.get("clipboard_count_1min", 0) / 10.0)
        features.append(history_context.get("screenshot_count_1min", 0) / 10.0)
        features.append(history_context.get("file_transfer_count_1min", 0) / 10.0)
        features.append(history_context.get("clipboard_total_kb_1min", 0) / 1000.0)
        features.append(history_context.get("file_transfer_total_mb_1min", 0))
        
        return np.array(features).reshape(1, -1)
    
    def predict(self, event: Dict, history_context: Dict) -> Tuple[float, Dict]:
        """Predict anomaly score"""
        if self.model is None:
            # Stub: return random score for testing
            import random
            score = random.uniform(0.3, 0.7)
            return score, {"error": "Model not loaded, using stub"}
        
        try:
            features = self.extract_features(event, history_context)
            score = self.model.predict_proba(features)[0][1]
            
            # Feature importance
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


class DetectionEngine:
    """Main detection engine combining rules + ML"""
    
    def __init__(self):
        self.rule_detector = RuleBasedDetector()
        self.ml_detector = MLDetectorStub()
        self.history_window = deque(maxlen=1000)
    
    def get_history_context(self, current_time: float) -> Dict:
        """Get historical context for ML features"""
        one_minute_ago = current_time - 60
        
        recent_events = [
            e for e in self.history_window
            if e.get("timestamp", 0) >= one_minute_ago
        ]
        
        return {
            "clipboard_count_1min": sum(1 for e in recent_events if e.get("event_type") == "clipboard_copy"),
            "screenshot_count_1min": sum(1 for e in recent_events if e.get("event_type") == "screenshot"),
            "file_transfer_count_1min": sum(1 for e in recent_events if e.get("event_type") == "file_transfer"),
            "clipboard_total_kb_1min": sum(e.get("size_kb", 0) for e in recent_events if e.get("event_type") == "clipboard_copy"),
            "file_transfer_total_mb_1min": sum(e.get("size_mb", 0) for e in recent_events if e.get("event_type") == "file_transfer"),
        }
    
    def evaluate(self, event: Dict) -> Dict:
        """Evaluate event and return detection result"""
        # Update history
        self.history_window.append(event)
        
        # Rule-based detection
        rule_alert, rule_reasons = self.rule_detector.evaluate(event)
        
        # ML-based detection
        history_context = self.get_history_context(event.get("timestamp", time.time()))
        ml_score, ml_info = self.ml_detector.predict(event, history_context)
        ml_alert = ml_score > 0.5
        
        # Combine results
        detection_methods = []
        reasons = []
        
        if rule_alert:
            detection_methods.append("rule_based")
            reasons.extend(rule_reasons)
        
        if ml_alert:
            detection_methods.append("ml_based")
            reasons.append(f"ML anomaly score: {ml_score:.3f} (threshold: 0.5)")
        
        is_alert = rule_alert or ml_alert
        
        severity = "high" if rule_alert and ml_alert else ("medium" if is_alert else "low")
        
        return {
            "is_alert": is_alert,
            "detection_methods": detection_methods,
            "reasons": reasons,
            "severity": severity,
            "ml_score": ml_score,
            "ml_info": ml_info
        }


# Global instance
detection_engine = DetectionEngine()

