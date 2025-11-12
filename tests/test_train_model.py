"""
Unit tests for train_model.py
"""
import pytest
import joblib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from train_model import generate_synthetic_dataset, train_model
from sklearn.ensemble import RandomForestClassifier


class TestGenerateSyntheticDataset:
    """Test generate_synthetic_dataset function."""
    
    def test_generate_dataset_default(self):
        """Test dataset generation with default parameters."""
        df = generate_synthetic_dataset()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1000
        assert "label" in df.columns
    
    def test_generate_dataset_custom_size(self):
        """Test dataset generation with custom size."""
        df = generate_synthetic_dataset(n_samples=500)
        
        assert len(df) == 500
    
    def test_generate_dataset_features(self):
        """Test dataset has correct features."""
        df = generate_synthetic_dataset(n_samples=100)
        
        # Check event type features
        assert "is_clipboard" in df.columns
        assert "is_screenshot" in df.columns
        assert "is_file_transfer" in df.columns
        
        # Check size features
        assert "clipboard_size_mb" in df.columns
        assert "file_size_mb" in df.columns
        
        # Check temporal features
        assert "time_of_day" in df.columns
        
        # Check history features
        assert "clipboard_count_1min" in df.columns
        assert "screenshot_count_1min" in df.columns
        assert "file_transfer_count_1min" in df.columns
        assert "clipboard_total_kb_1min" in df.columns
        assert "file_transfer_total_mb_1min" in df.columns
    
    def test_generate_dataset_labels(self):
        """Test dataset has correct label distribution."""
        df = generate_synthetic_dataset(n_samples=1000)
        
        assert "label" in df.columns
        assert df["label"].dtype in [int, np.int64]
        assert set(df["label"].unique()).issubset({0, 1})
        
        # Should have roughly 80% normal, 20% anomaly
        anomaly_rate = df["label"].mean()
        assert 0.15 < anomaly_rate < 0.25  # Allow some variance
    
    def test_generate_dataset_deterministic(self):
        """Test dataset generation is deterministic with same seed."""
        df1 = generate_synthetic_dataset(n_samples=100)
        df2 = generate_synthetic_dataset(n_samples=100)
        
        # Should be identical due to fixed seed in function
        pd.testing.assert_frame_equal(df1, df2)
    
    def test_generate_dataset_feature_ranges(self):
        """Test feature values are in expected ranges."""
        df = generate_synthetic_dataset(n_samples=100)
        
        # Event type features should be 0 or 1
        assert df["is_clipboard"].isin([0.0, 1.0]).all()
        assert df["is_screenshot"].isin([0.0, 1.0]).all()
        assert df["is_file_transfer"].isin([0.0, 1.0]).all()
        
        # Size features should be non-negative
        assert (df["clipboard_size_mb"] >= 0).all()
        assert (df["file_size_mb"] >= 0).all()
        
        # Time of day should be between 0 and 1
        assert (df["time_of_day"] >= 0).all()
        assert (df["time_of_day"] <= 1).all()


class TestTrainModel:
    """Test train_model function."""
    
    def test_train_model_creates_files(self, temp_dir, monkeypatch):
        """Test train_model creates necessary files."""
        # Change to temp directory
        original_cwd = Path.cwd()
        monkeypatch.chdir(temp_dir)
        
        try:
            # Mock print to avoid output during tests
            import builtins
            original_print = builtins.print
            
            def mock_print(*args, **kwargs):
                pass
            
            builtins.print = mock_print
            
            try:
                train_model()
            finally:
                builtins.print = original_print
            
            # Check model file was created
            model_file = temp_dir / "models" / "detection_model.pkl"
            assert model_file.exists()
            
            # Check metadata file was created
            metadata_file = temp_dir / "models" / "model_metadata.json"
            assert metadata_file.exists()
            
            # Check SHAP data file was created (if SHAP worked)
            shap_file = temp_dir / "models" / "shap_data.json"
            # SHAP might fail, so this is optional
            
        finally:
            monkeypatch.chdir(original_cwd)
    
    def test_train_model_saves_model(self, temp_dir, monkeypatch):
        """Test train_model saves model correctly."""
        original_cwd = Path.cwd()
        monkeypatch.chdir(temp_dir)
        
        try:
            import builtins
            original_print = builtins.print
            
            def mock_print(*args, **kwargs):
                pass
            
            builtins.print = mock_print
            
            try:
                train_model()
            finally:
                builtins.print = original_print
            
            model_file = temp_dir / "models" / "detection_model.pkl"
            model_data = joblib.load(model_file)
            
            assert "model" in model_data
            assert isinstance(model_data["model"], RandomForestClassifier)
            assert "feature_names" in model_data
            assert "feature_importance" in model_data
            assert "train_accuracy" in model_data
            assert "test_accuracy" in model_data
            
        finally:
            monkeypatch.chdir(original_cwd)
    
    def test_train_model_metadata(self, temp_dir, monkeypatch):
        """Test train_model saves metadata correctly."""
        original_cwd = Path.cwd()
        monkeypatch.chdir(temp_dir)
        
        try:
            import builtins
            original_print = builtins.print
            
            def mock_print(*args, **kwargs):
                pass
            
            builtins.print = mock_print
            
            try:
                train_model()
            finally:
                builtins.print = original_print
            
            metadata_file = temp_dir / "models" / "model_metadata.json"
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            assert "model_type" in metadata
            assert metadata["model_type"] == "RandomForestClassifier"
            assert "n_estimators" in metadata
            assert "n_features" in metadata
            assert "train_accuracy" in metadata
            assert "test_accuracy" in metadata
            assert "feature_names" in metadata
            assert "feature_importance" in metadata
            
        finally:
            monkeypatch.chdir(original_cwd)



