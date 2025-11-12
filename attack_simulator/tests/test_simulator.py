"""
Tests for attack simulator scripts
"""
import pytest
import json
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def test_clipboard_sim():
    """Test clipboard simulation"""
    from attack_simulator.clipboard_sim import generate_clipboard_event, simulate_clipboard_abuse
    
    # Test event generation
    event = generate_clipboard_event(size_kb=500)
    assert event["event_type"] == "clipboard_copy"
    assert event["size_kb"] == 500
    assert "BENIGN SIMULATION" in event.get("note", "")
    
    # Test simulation
    output_dir = "data/synthetic_test"
    events = simulate_clipboard_abuse(output_dir=output_dir, burst_size=3, size_kb=300)
    assert len(events) == 3
    
    # Cleanup
    test_file = Path(output_dir) / "vnc_events.jsonl"
    if test_file.exists():
        test_file.unlink()


def test_screenshot_sim():
    """Test screenshot simulation"""
    from attack_simulator.screenshot_burst_sim import generate_screenshot_event, simulate_screenshot_burst
    
    # Test event generation
    event = generate_screenshot_event(timestamp=1000.0)
    assert event["event_type"] == "screenshot"
    assert "BENIGN SIMULATION" in event.get("note", "")
    
    # Test simulation
    output_dir = "data/synthetic_test"
    events = simulate_screenshot_burst(output_dir=output_dir, count=5, interval_seconds=1.0)
    assert len(events) == 5
    
    # Cleanup
    test_file = Path(output_dir) / "vnc_events.jsonl"
    if test_file.exists():
        test_file.unlink()


def test_file_transfer_sim():
    """Test file transfer simulation"""
    from attack_simulator.file_transfer_sim import generate_file_transfer_event, simulate_file_exfiltration
    
    # Test event generation
    event = generate_file_transfer_event(filename="test.zip", size_mb=100.0)
    assert event["event_type"] == "file_transfer"
    assert event["size_mb"] == 100.0
    assert "BENIGN SIMULATION" in event.get("note", "")
    
    # Test simulation
    output_dir = "data/synthetic_test"
    events = simulate_file_exfiltration(output_dir=output_dir, file_count=2, size_mb=50.0)
    assert len(events) == 2
    
    # Cleanup
    test_file = Path(output_dir) / "vnc_events.jsonl"
    if test_file.exists():
        test_file.unlink()

