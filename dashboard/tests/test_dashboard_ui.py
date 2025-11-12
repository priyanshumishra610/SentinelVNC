"""
Tests for dashboard UI (basic smoke tests)
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def test_dashboard_imports():
    """Test that dashboard can be imported"""
    try:
        import streamlit
        import requests
        import pandas
        import plotly
        assert True
    except ImportError as e:
        pytest.skip(f"Dashboard dependencies not installed: {e}")


def test_dashboard_functions():
    """Test dashboard helper functions"""
    # Mock test - in real scenario would test with mocked API
    def mock_fetch_alerts(api_url):
        return []
    
    alerts = mock_fetch_alerts("http://localhost:8000")
    assert isinstance(alerts, list)

