#!/usr/bin/env python3
"""
Clipboard Simulation Script
Safe script to simulate large clipboard events (writes JSON event).
This is a benign simulation tool for testing detection capabilities.
"""
import json
import time
import random
from pathlib import Path
from typing import Dict, List


def generate_clipboard_event(size_kb: int, timestamp: float = None) -> Dict:
    """Generate a clipboard copy event"""
    if timestamp is None:
        timestamp = time.time()
    
    return {
        "event_type": "clipboard_copy",
        "timestamp": timestamp,
        "size_bytes": size_kb * 1024,
        "size_kb": size_kb,
        "content_preview": f"[{size_kb}KB of synthetic data]",
        "source": "vnc_client",
        "note": "BENIGN SIMULATION - Safe for testing"
    }


def simulate_clipboard_abuse(
    output_dir: str = "data/synthetic",
    burst_size: int = 5,
    size_kb: int = 500
) -> List[Dict]:
    """
    Simulate clipboard abuse (large data exfiltration pattern).
    This is a safe, benign simulation.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    events_file = output_path / "vnc_events.jsonl"
    
    print(f"[Clipboard Sim] Simulating clipboard abuse: {burst_size} events of {size_kb}KB each")
    print("[Clipboard Sim] NOTE: This is a benign simulation for testing only")
    
    events = []
    base_time = time.time()
    
    for i in range(burst_size):
        event = generate_clipboard_event(
            size_kb=size_kb,
            timestamp=base_time + i * 0.5  # Rapid succession
        )
        events.append(event)
        
        # Write to file
        with open(events_file, 'a') as f:
            f.write(json.dumps(event) + '\n')
    
    print(f"[Clipboard Sim] Generated {len(events)} events, saved to {events_file}")
    return events


if __name__ == "__main__":
    # Run simulation
    events = simulate_clipboard_abuse(burst_size=5, size_kb=500)
    print(f"Generated {len(events)} clipboard events")

