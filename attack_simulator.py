#!/usr/bin/env python3
"""
SentinelVNC Attack Simulator
Generates synthetic VNC events to simulate data exfiltration attacks.
This is a benign simulation tool for testing detection capabilities.
"""

import json
import time
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from PIL import Image, ImageDraw
import numpy as np


class AttackSimulator:
    """Simulates various VNC attack patterns for testing detection."""
    
    def __init__(self, output_dir: str = "data/synthetic"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.events_file = self.output_dir / "vnc_events.jsonl"
        self.screenshot_dir = self.output_dir / "screenshots"
        self.screenshot_dir.mkdir(exist_ok=True)
        
    def generate_clipboard_event(self, size_kb: int, timestamp: Optional[float] = None) -> Dict:
        """Generate a clipboard copy event."""
        if timestamp is None:
            timestamp = time.time()
        
        return {
            "event_type": "clipboard_copy",
            "timestamp": timestamp,
            "size_bytes": size_kb * 1024,
            "size_kb": size_kb,
            "content_preview": f"[{size_kb}KB of data]",
            "source": "vnc_client"
        }
    
    def generate_screenshot_event(self, timestamp: Optional[float] = None) -> Dict:
        """Generate a screenshot capture event."""
        if timestamp is None:
            timestamp = time.time()
        
        # Create a simple synthetic screenshot
        img = Image.new('RGB', (1920, 1080), color='white')
        draw = ImageDraw.Draw(img)
        draw.rectangle([100, 100, 1820, 980], fill='lightblue', outline='black', width=2)
        draw.text((960, 540), f"Screenshot {int(timestamp)}", fill='black', anchor='mm')
        
        screenshot_path = self.screenshot_dir / f"screenshot_{int(timestamp)}.png"
        img.save(screenshot_path)
        
        return {
            "event_type": "screenshot",
            "timestamp": timestamp,
            "screenshot_path": str(screenshot_path),
            "resolution": "1920x1080",
            "source": "vnc_client"
        }
    
    def generate_file_transfer_event(self, filename: str, size_mb: float, 
                                     timestamp: Optional[float] = None) -> Dict:
        """Generate a file transfer event."""
        if timestamp is None:
            timestamp = time.time()
        
        return {
            "event_type": "file_transfer",
            "timestamp": timestamp,
            "filename": filename,
            "size_bytes": int(size_mb * 1024 * 1024),
            "size_mb": size_mb,
            "source": "vnc_client"
        }
    
    def simulate_normal_activity(self, duration_seconds: int = 60) -> List[Dict]:
        """Simulate normal VNC usage patterns."""
        events = []
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        current_time = start_time
        
        while current_time < end_time:
            # Normal clipboard operations (small, infrequent)
            if random.random() < 0.1:  # 10% chance every iteration
                events.append(self.generate_clipboard_event(
                    size_kb=random.randint(1, 50),
                    timestamp=current_time
                ))
            
            # Normal screenshots (occasional)
            if random.random() < 0.05:  # 5% chance
                events.append(self.generate_screenshot_event(timestamp=current_time))
            
            current_time += random.uniform(2, 10)  # Wait 2-10 seconds between events
        
        return events
    
    def simulate_clipboard_abuse(self, burst_size: int = 5, 
                                 size_kb: int = 500) -> List[Dict]:
        """Simulate clipboard abuse (large data exfiltration)."""
        events = []
        base_time = time.time()
        
        for i in range(burst_size):
            events.append(self.generate_clipboard_event(
                size_kb=size_kb,
                timestamp=base_time + i * 0.5  # Rapid succession
            ))
        
        return events
    
    def simulate_screenshot_scraping(self, count: int = 10, 
                                     interval_seconds: float = 1.0) -> List[Dict]:
        """Simulate screenshot scraping attack."""
        events = []
        base_time = time.time()
        
        for i in range(count):
            events.append(self.generate_screenshot_event(
                timestamp=base_time + i * interval_seconds
            ))
        
        return events
    
    def simulate_file_exfiltration(self, file_count: int = 3, 
                                   size_mb: float = 100.0) -> List[Dict]:
        """Simulate file transfer exfiltration."""
        events = []
        base_time = time.time()
        
        for i in range(file_count):
            events.append(self.generate_file_transfer_event(
                filename=f"sensitive_data_{i}.zip",
                size_mb=size_mb,
                timestamp=base_time + i * 2.0
            ))
        
        return events
    
    def save_events(self, events: List[Dict]):
        """Save events to JSONL file (one event per line)."""
        with open(self.events_file, 'a') as f:
            for event in events:
                f.write(json.dumps(event) + '\n')
    
    def run_attack_scenario(self, scenario: str = "mixed"):
        """
        Run a predefined attack scenario.
        
        Scenarios:
        - "normal": Normal user activity
        - "clipboard_abuse": Large clipboard operations
        - "screenshot_scraping": Rapid screenshot capture
        - "file_exfiltration": Large file transfers
        - "mixed": Combination of attacks
        """
        print(f"[Simulator] Running scenario: {scenario}")
        
        if scenario == "normal":
            events = self.simulate_normal_activity(duration_seconds=30)
        elif scenario == "clipboard_abuse":
            events = self.simulate_clipboard_abuse(burst_size=5, size_kb=500)
        elif scenario == "screenshot_scraping":
            events = self.simulate_screenshot_scraping(count=10, interval_seconds=0.5)
        elif scenario == "file_exfiltration":
            events = self.simulate_file_exfiltration(file_count=3, size_mb=100.0)
        elif scenario == "mixed":
            # Mix of normal and attack patterns
            events = []
            events.extend(self.simulate_normal_activity(duration_seconds=20))
            time.sleep(1)
            events.extend(self.simulate_clipboard_abuse(burst_size=3, size_kb=300))
            time.sleep(1)
            events.extend(self.simulate_screenshot_scraping(count=8, interval_seconds=0.8))
            events.extend(self.simulate_file_exfiltration(file_count=2, size_mb=50.0))
        else:
            raise ValueError(f"Unknown scenario: {scenario}")
        
        self.save_events(events)
        print(f"[Simulator] Generated {len(events)} events")
        return events


if __name__ == "__main__":
    # Test the simulator
    sim = AttackSimulator()
    
    print("Testing attack simulator...")
    print("\n1. Normal activity:")
    sim.run_attack_scenario("normal")
    
    print("\n2. Clipboard abuse:")
    sim.run_attack_scenario("clipboard_abuse")
    
    print("\n3. Screenshot scraping:")
    sim.run_attack_scenario("screenshot_scraping")
    
    print("\n4. File exfiltration:")
    sim.run_attack_scenario("file_exfiltration")
    
    print("\n5. Mixed attack scenario:")
    sim.run_attack_scenario("mixed")
    
    print(f"\n[Simulator] All events saved to {sim.events_file}")


