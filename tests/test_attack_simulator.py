"""
Unit tests for attack_simulator.py
"""
import pytest
import json
import time
from pathlib import Path
from attack_simulator import AttackSimulator


class TestAttackSimulator:
    """Test AttackSimulator class."""
    
    def test_init(self, temp_dir):
        """Test AttackSimulator initialization."""
        sim = AttackSimulator(output_dir=str(temp_dir / "data" / "synthetic"))
        assert sim.output_dir.exists()
        assert sim.events_file.exists() or sim.events_file.parent.exists()
        assert sim.screenshot_dir.exists()
    
    def test_generate_clipboard_event(self, temp_dir):
        """Test clipboard event generation."""
        sim = AttackSimulator(output_dir=str(temp_dir / "data" / "synthetic"))
        event = sim.generate_clipboard_event(size_kb=250)
        
        assert event["event_type"] == "clipboard_copy"
        assert event["size_kb"] == 250
        assert event["size_bytes"] == 250 * 1024
        assert "timestamp" in event
        assert event["source"] == "vnc_client"
    
    def test_generate_screenshot_event(self, temp_dir):
        """Test screenshot event generation."""
        sim = AttackSimulator(output_dir=str(temp_dir / "data" / "synthetic"))
        event = sim.generate_screenshot_event()
        
        assert event["event_type"] == "screenshot"
        assert "timestamp" in event
        assert "screenshot_path" in event
        assert event["resolution"] == "1920x1080"
        assert Path(event["screenshot_path"]).exists()
    
    def test_generate_file_transfer_event(self, temp_dir):
        """Test file transfer event generation."""
        sim = AttackSimulator(output_dir=str(temp_dir / "data" / "synthetic"))
        event = sim.generate_file_transfer_event(filename="test.zip", size_mb=75.0)
        
        assert event["event_type"] == "file_transfer"
        assert event["filename"] == "test.zip"
        assert event["size_mb"] == 75.0
        assert event["size_bytes"] == int(75.0 * 1024 * 1024)
        assert "timestamp" in event
    
    def test_simulate_clipboard_abuse(self, temp_dir):
        """Test clipboard abuse simulation."""
        sim = AttackSimulator(output_dir=str(temp_dir / "data" / "synthetic"))
        events = sim.simulate_clipboard_abuse(burst_size=3, size_kb=400)
        
        assert len(events) == 3
        assert all(e["event_type"] == "clipboard_copy" for e in events)
        assert all(e["size_kb"] == 400 for e in events)
    
    def test_simulate_screenshot_scraping(self, temp_dir):
        """Test screenshot scraping simulation."""
        sim = AttackSimulator(output_dir=str(temp_dir / "data" / "synthetic"))
        events = sim.simulate_screenshot_scraping(count=5, interval_seconds=0.5)
        
        assert len(events) == 5
        assert all(e["event_type"] == "screenshot" for e in events)
        # Check timestamps are increasing
        timestamps = [e["timestamp"] for e in events]
        assert timestamps == sorted(timestamps)
    
    def test_simulate_file_exfiltration(self, temp_dir):
        """Test file exfiltration simulation."""
        sim = AttackSimulator(output_dir=str(temp_dir / "data" / "synthetic"))
        events = sim.simulate_file_exfiltration(file_count=2, size_mb=80.0)
        
        assert len(events) == 2
        assert all(e["event_type"] == "file_transfer" for e in events)
        assert all(e["size_mb"] == 80.0 for e in events)
    
    def test_save_events(self, temp_dir):
        """Test saving events to file."""
        sim = AttackSimulator(output_dir=str(temp_dir / "data" / "synthetic"))
        events = [
            sim.generate_clipboard_event(size_kb=100),
            sim.generate_screenshot_event()
        ]
        
        sim.save_events(events)
        
        assert sim.events_file.exists()
        with open(sim.events_file, 'r') as f:
            lines = f.readlines()
            assert len(lines) == 2
            for line in lines:
                event = json.loads(line.strip())
                assert "event_type" in event
    
    def test_run_attack_scenario_normal(self, temp_dir):
        """Test normal scenario."""
        sim = AttackSimulator(output_dir=str(temp_dir / "data" / "synthetic"))
        events = sim.run_attack_scenario("normal")
        
        assert len(events) > 0
        assert sim.events_file.exists()
    
    def test_run_attack_scenario_clipboard_abuse(self, temp_dir):
        """Test clipboard abuse scenario."""
        sim = AttackSimulator(output_dir=str(temp_dir / "data" / "synthetic"))
        events = sim.run_attack_scenario("clipboard_abuse")
        
        assert len(events) > 0
        assert any(e["event_type"] == "clipboard_copy" for e in events)
    
    def test_run_attack_scenario_screenshot_scraping(self, temp_dir):
        """Test screenshot scraping scenario."""
        sim = AttackSimulator(output_dir=str(temp_dir / "data" / "synthetic"))
        events = sim.run_attack_scenario("screenshot_scraping")
        
        assert len(events) > 0
        assert any(e["event_type"] == "screenshot" for e in events)
    
    def test_run_attack_scenario_file_exfiltration(self, temp_dir):
        """Test file exfiltration scenario."""
        sim = AttackSimulator(output_dir=str(temp_dir / "data" / "synthetic"))
        events = sim.run_attack_scenario("file_exfiltration")
        
        assert len(events) > 0
        assert any(e["event_type"] == "file_transfer" for e in events)
    
    def test_run_attack_scenario_mixed(self, temp_dir):
        """Test mixed attack scenario."""
        sim = AttackSimulator(output_dir=str(temp_dir / "data" / "synthetic"))
        events = sim.run_attack_scenario("mixed")
        
        assert len(events) > 0
        event_types = [e["event_type"] for e in events]
        assert "clipboard_copy" in event_types
        assert "screenshot" in event_types
        assert "file_transfer" in event_types
    
    def test_run_attack_scenario_invalid(self, temp_dir):
        """Test invalid scenario raises error."""
        sim = AttackSimulator(output_dir=str(temp_dir / "data" / "synthetic"))
        with pytest.raises(ValueError):
            sim.run_attack_scenario("invalid_scenario")



