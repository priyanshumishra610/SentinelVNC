#!/usr/bin/env python3
"""
SentinelVNC ML Model Training
Trains a lightweight anomaly detection model with SHAP explainability.
"""

import numpy as np
import pandas as pd
from pathlib import Path
import joblib
import json
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import shap


def generate_synthetic_dataset(n_samples: int = 1000) -> pd.DataFrame:
    """Generate synthetic training dataset."""
    np.random.seed(42)
    
    data = []
    
    for i in range(n_samples):
        # Random event type
        event_type = np.random.choice(["clipboard_copy", "screenshot", "file_transfer"], 
                                     p=[0.4, 0.3, 0.3])
        
        # Normal vs anomaly (80% normal, 20% anomaly)
        is_anomaly = np.random.choice([0, 1], p=[0.8, 0.2])
        
        # Feature extraction (matching detector.py)
        features = {}
        features["is_clipboard"] = 1.0 if event_type == "clipboard_copy" else 0.0
        features["is_screenshot"] = 1.0 if event_type == "screenshot" else 0.0
        features["is_file_transfer"] = 1.0 if event_type == "file_transfer" else 0.0
        
        if event_type == "clipboard_copy":
            if is_anomaly:
                size_kb = np.random.uniform(200, 1000)  # Large clipboard
            else:
                size_kb = np.random.uniform(1, 100)  # Normal clipboard
            features["clipboard_size_mb"] = size_kb / 1000.0
            features["file_size_mb"] = 0.0
        elif event_type == "file_transfer":
            if is_anomaly:
                size_mb = np.random.uniform(50, 500)  # Large file
            else:
                size_mb = np.random.uniform(1, 20)  # Normal file
            features["clipboard_size_mb"] = 0.0
            features["file_size_mb"] = size_mb
        else:
            features["clipboard_size_mb"] = 0.0
            features["file_size_mb"] = 0.0
        
        # Temporal features
        features["time_of_day"] = np.random.uniform(0, 1)
        
        # History features (simulated)
        if is_anomaly:
            features["clipboard_count_1min"] = np.random.uniform(5, 20) / 10.0
            features["screenshot_count_1min"] = np.random.uniform(5, 15) / 10.0
            features["file_transfer_count_1min"] = np.random.uniform(2, 10) / 10.0
            features["clipboard_total_kb_1min"] = np.random.uniform(500, 2000) / 1000.0
            features["file_transfer_total_mb_1min"] = np.random.uniform(50, 300)
        else:
            features["clipboard_count_1min"] = np.random.uniform(0, 5) / 10.0
            features["screenshot_count_1min"] = np.random.uniform(0, 3) / 10.0
            features["file_transfer_count_1min"] = np.random.uniform(0, 2) / 10.0
            features["clipboard_total_kb_1min"] = np.random.uniform(0, 200) / 1000.0
            features["file_transfer_total_mb_1min"] = np.random.uniform(0, 30)
        
        features["label"] = is_anomaly
        data.append(features)
    
    return pd.DataFrame(data)


def train_model():
    """Train the anomaly detection model."""
    print("=" * 60)
    print("SentinelVNC ML Model Training")
    print("=" * 60)
    
    # Create directories
    Path("models").mkdir(exist_ok=True)
    Path("data/synthetic").mkdir(parents=True, exist_ok=True)
    
    # Generate dataset
    print("\n1. Generating synthetic dataset...")
    df = generate_synthetic_dataset(n_samples=2000)
    print(f"   Generated {len(df)} samples")
    print(f"   Anomalies: {df['label'].sum()} ({df['label'].mean()*100:.1f}%)")
    
    # Prepare features
    feature_columns = [col for col in df.columns if col != "label"]
    X = df[feature_columns].values
    y = df["label"].values
    
    print(f"\n2. Features: {len(feature_columns)}")
    print(f"   {feature_columns}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\n3. Training set: {len(X_train)} samples")
    print(f"   Test set: {len(X_test)} samples")
    
    # Train model
    print("\n4. Training RandomForest classifier...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    print("\n5. Evaluating model...")
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["Normal", "Anomaly"]))
    
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    
    # Feature importance
    print("\n6. Feature Importance:")
    feature_importance = dict(zip(feature_columns, model.feature_importances_))
    for feature, importance in sorted(feature_importance.items(), 
                                     key=lambda x: x[1], reverse=True):
        print(f"   {feature:30s}: {importance:.4f}")
    
    # SHAP explainability
    print("\n7. Computing SHAP values (sample of 100)...")
    try:
        # Use a subset for SHAP (it can be slow)
        shap_sample_size = min(100, len(X_test))
        X_test_sample = X_test[:shap_sample_size]
        
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_test_sample)
        
        # Save SHAP summary plot data
        shap_data = {
            "shap_values": shap_values[1].tolist() if isinstance(shap_values, list) else shap_values.tolist(),
            "feature_names": feature_columns,
            "sample_size": shap_sample_size
        }
        
        shap_file = Path("models/shap_data.json")
        with open(shap_file, 'w') as f:
            json.dump(shap_data, f)
        
        print(f"   SHAP values saved to {shap_file}")
        
        # Print example SHAP values for first prediction
        if isinstance(shap_values, list):
            shap_vals = shap_values[1][0]
        else:
            shap_vals = shap_values[0]
        
        print("\n   Example SHAP values (first test sample):")
        for feature, shap_val in zip(feature_columns, shap_vals):
            print(f"     {feature:30s}: {shap_val:8.4f}")
    
    except Exception as e:
        print(f"   Warning: SHAP computation failed: {e}")
        print("   Continuing without SHAP data...")
    
    # Save model
    print("\n8. Saving model...")
    model_data = {
        "model": model,
        "feature_names": feature_columns,
        "feature_importance": feature_importance,
        "train_accuracy": model.score(X_train, y_train),
        "test_accuracy": model.score(X_test, y_test)
    }
    
    model_path = Path("models/detection_model.pkl")
    joblib.dump(model_data, model_path)
    print(f"   Model saved to {model_path}")
    
    # Save metadata
    metadata = {
        "model_type": "RandomForestClassifier",
        "n_estimators": 100,
        "max_depth": 10,
        "n_features": len(feature_columns),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "train_accuracy": float(model.score(X_train, y_train)),
        "test_accuracy": float(model.score(X_test, y_test)),
        "feature_names": feature_columns,
        "feature_importance": {k: float(v) for k, v in feature_importance.items()}
    }
    
    metadata_path = Path("models/model_metadata.json")
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"   Metadata saved to {metadata_path}")
    
    print("\n" + "=" * 60)
    print("Training complete!")
    print("=" * 60)


if __name__ == "__main__":
    train_model()



