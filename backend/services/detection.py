"""
Hybrid detection service (Rules + ML + DL)
"""
import time
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import numpy as np
import pandas as pd
from collections import deque
import joblib

# Import existing detectors
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
try:
    from detector import RuleBasedDetector, MLDetector
except ImportError:
    # Fallback if detector.py not found
    print("[Warning] Could not import detector.py, using fallback")
    RuleBasedDetector = None
    MLDetector = None


class DLDetector:
    """Deep Learning detector using LSTM/Autoencoder"""
    
    def __init__(self, model_path: str = "models/dl_anomaly_model.h5"):
        self.model_path = Path(model_path)
        self.model = None
        self.scaler = None
        self.sequence_length = 10
        self.load_model()
    
    def load_model(self):
        """Load trained DL model"""
        try:
            import tensorflow as tf
            from tensorflow import keras
            
            if self.model_path.exists():
                self.model = keras.models.load_model(self.model_path)
                print(f"[DLDetector] Loaded model from {self.model_path}")
            else:
                print(f"[DLDetector] Model not found at {self.model_path}, using fallback")
                self.model = None
        except ImportError:
            print("[DLDetector] TensorFlow not available, DL detection disabled")
            self.model = None
        except Exception as e:
            print(f"[DLDetector] Error loading model: {e}")
            self.model = None
    
    def extract_sequence_features(self, event: Dict, history: List[Dict]) -> np.ndarray:
        """Extract sequence features for LSTM"""
        # Build sequence from history
        sequence = []
        for hist_event in history[-self.sequence_length:]:
            features = self._extract_features(hist_event)
            sequence.append(features)
        
        # Pad or truncate to sequence_length
        while len(sequence) < self.sequence_length:
            sequence.insert(0, np.zeros(len(sequence[0]) if sequence else 10))
        
        sequence = sequence[-self.sequence_length:]
        
        # Add current event
        current_features = self._extract_features(event)
        sequence.append(current_features)
        sequence = sequence[-self.sequence_length:]
        
        return np.array(sequence).reshape(1, self.sequence_length, -1)
    
    def _extract_features(self, event: Dict) -> np.ndarray:
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
        timestamp = event.get("timestamp", time.time())
        features.append(timestamp % 86400 / 86400.0)  # Time of day
        
        # Rate features
        features.append(event.get("size_kb", 0) / 1000.0)
        features.append(event.get("size_mb", 0))
        
        return np.array(features)
    
    def predict(self, event: Dict, history: List[Dict]) -> Tuple[float, Dict]:
        """Predict anomaly score using DL model"""
        if self.model is None:
            return 0.0, {"error": "Model not loaded"}
        
        try:
            # Extract sequence features
            sequence = self.extract_sequence_features(event, history)
            
            # Predict
            if hasattr(self.model, 'predict'):
                prediction = self.model.predict(sequence, verbose=0)
                # For autoencoder, use reconstruction error
                if len(prediction.shape) > 1:
                    # Reconstruction error
                    reconstruction_error = np.mean(np.square(sequence - prediction))
                    score = min(1.0, reconstruction_error * 10)  # Normalize
                else:
                    score = float(prediction[0][0] if prediction.ndim > 1 else prediction[0])
            else:
                score = 0.0
            
            return float(score), {
                "anomaly_score": float(score),
                "model_type": "LSTM/Autoencoder",
                "threshold": 0.5
            }
        except Exception as e:
            print(f"[DLDetector] Prediction error: {e}")
            return 0.0, {"error": str(e)}


class EnhancedDetectionService:
    """Enhanced detection service with Rules + ML + DL"""
    
    def __init__(self):
        if RuleBasedDetector:
            self.rule_detector = RuleBasedDetector()
        else:
            self.rule_detector = None
        if MLDetector:
            self.ml_detector = MLDetector()
        else:
            self.ml_detector = None
        self.dl_detector = DLDetector()
        self.history_window = deque(maxlen=1000)
        self.forensic_dir = Path("forensic")
        self.forensic_dir.mkdir(parents=True, exist_ok=True)
    
    def get_history_context(self, current_time: float) -> Dict:
        """Get historical context for ML features"""
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
    
    def process_event(self, event: Dict) -> Dict:
        """Process event with hybrid detection"""
        # Update history
        self.history_window.append(event)
        
        # Rule-based detection
        if self.rule_detector:
            rule_alert, rule_reasons = self.rule_detector.evaluate_rules(event)
        else:
            rule_alert, rule_reasons = False, []
        
        # ML-based detection
        if self.ml_detector:
            history_context = self.get_history_context(event.get("timestamp", time.time()))
            ml_score, ml_info = self.ml_detector.predict(event, history_context)
            ml_alert = ml_score > 0.5
        else:
            ml_score, ml_info = 0.0, {}
            ml_alert = False
        
        # DL-based detection
        history_list = list(self.history_window)
        dl_score, dl_info = self.dl_detector.predict(event, history_list)
        dl_alert = dl_score > 0.5
        
        # Combine results (ensemble voting)
        detection_methods = []
        reasons = []
        
        if rule_alert:
            detection_methods.append("rule_based")
            reasons.extend([f"Rule: {r}" for r in rule_reasons])
        
        if ml_alert:
            detection_methods.append("ml_based")
            reasons.append(f"ML anomaly score: {ml_score:.3f} (threshold: 0.5)")
        
        if dl_alert:
            detection_methods.append("dl_based")
            reasons.append(f"DL anomaly score: {dl_score:.3f} (threshold: 0.5)")
        
        # Determine if alert
        is_alert = rule_alert or ml_alert or dl_alert
        
        # Determine severity
        if rule_alert and (ml_alert or dl_alert):
            severity = "high"
        elif ml_alert and dl_alert:
            severity = "high"
        elif rule_alert or ml_alert or dl_alert:
            severity = "medium"
        else:
            severity = "low"
        
        result = {
            "is_alert": is_alert,
            "detection_methods": detection_methods,
            "reasons": reasons,
            "severity": severity,
            "ml_score": ml_score,
            "dl_score": dl_score,
            "ml_info": ml_info,
            "dl_info": dl_info
        }
        
        if is_alert:
            # Generate alert ID
            alert_id = f"ALERT_{int(time.time() * 1000)}"
            result["alert_id"] = alert_id
            
            # Generate forensic hash
            alert_str = json.dumps(result, sort_keys=True)
            result["forensic_hash"] = hashlib.sha256(alert_str.encode()).hexdigest()
        
        return result


# Global instance
DetectionService = EnhancedDetectionService

