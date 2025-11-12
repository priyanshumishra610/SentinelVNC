#!/usr/bin/env python3
"""
Screenshot Burst Simulation Script
Generate synthetic screenshots (images) and event messages.
This is a benign simulation tool for testing detection capabilities.
"""
import json
import time
from pathlib import Path
from typing import Dict, List
from PIL import Image, ImageDraw


def generate_screenshot_event(timestamp: float = None, screenshot_dir: Path = None) -> Dict:
    """Generate a screenshot capture event and create synthetic image"""
    if timestamp is None:
        timestamp = time.time()
    
    if screenshot_dir is None:
        screenshot_dir = Path("data/synthetic/screenshots")
    
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a simple synthetic screenshot
    img = Image.new('RGB', (1920, 1080), color='white')
    draw = ImageDraw.Draw(img)
    draw.rectangle([100, 100, 1820, 980], fill='lightblue', outline='black', width=2)
    draw.text((960, 540), f"Screenshot {int(timestamp)}", fill='black', anchor='mm')
    
    screenshot_path = screenshot_dir / f"screenshot_{int(timestamp)}.png"
    img.save(screenshot_path)
    
    return {
        "event_type": "screenshot",
        "timestamp": timestamp,
        "screenshot_path": str(screenshot_path),
        "resolution": "1920x1080",
        "source": "vnc_client",
        "note": "BENIGN SIMULATION - Safe for testing"
    }


def simulate_screenshot_burst(
    output_dir: str = "data/synthetic",
    count: int = 10,
    interval_seconds: float = 1.0
) -> List[Dict]:
    """
    Simulate screenshot scraping attack (rapid screenshot capture).
    This is a safe, benign simulation.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    events_file = output_path / "vnc_events.jsonl"
    screenshot_dir = output_path / "screenshots"
    
    print(f"[Screenshot Sim] Simulating screenshot burst: {count} screenshots every {interval_seconds}s")
    print("[Screenshot Sim] NOTE: This is a benign simulation for testing only")
    
    events = []
    base_time = time.time()
    
    for i in range(count):
        event = generate_screenshot_event(
            timestamp=base_time + i * interval_seconds,
            screenshot_dir=screenshot_dir
        )
        events.append(event)
        
        # Write to file
        with open(events_file, 'a') as f:
            f.write(json.dumps(event) + '\n')
    
    print(f"[Screenshot Sim] Generated {len(events)} events and {count} screenshot images")
    print(f"[Screenshot Sim] Saved to {events_file}")
    return events


if __name__ == "__main__":
    # Run simulation
    events = simulate_screenshot_burst(count=10, interval_seconds=0.5)
    print(f"Generated {len(events)} screenshot events")

