#!/usr/bin/env python3
"""
File Transfer Simulation Script
Simulate file transfer metadata events (no real exfiltration).
This is a benign simulation tool for testing detection capabilities.
"""
import json
import time
from pathlib import Path
from typing import Dict, List


def generate_file_transfer_event(
    filename: str,
    size_mb: float,
    timestamp: float = None
) -> Dict:
    """Generate a file transfer event (metadata only, no real file)"""
    if timestamp is None:
        timestamp = time.time()
    
    return {
        "event_type": "file_transfer",
        "timestamp": timestamp,
        "filename": filename,
        "size_bytes": int(size_mb * 1024 * 1024),
        "size_mb": size_mb,
        "source": "vnc_client",
        "note": "BENIGN SIMULATION - No actual file transfer, metadata only"
    }


def simulate_file_exfiltration(
    output_dir: str = "data/synthetic",
    file_count: int = 3,
    size_mb: float = 100.0
) -> List[Dict]:
    """
    Simulate file transfer exfiltration pattern.
    This is a safe, benign simulation - no actual files are transferred.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    events_file = output_path / "vnc_events.jsonl"
    
    print(f"[File Transfer Sim] Simulating file exfiltration: {file_count} files of {size_mb}MB each")
    print("[File Transfer Sim] NOTE: This is a benign simulation - no actual files are transferred")
    
    events = []
    base_time = time.time()
    
    for i in range(file_count):
        event = generate_file_transfer_event(
            filename=f"sensitive_data_{i}.zip",
            size_mb=size_mb,
            timestamp=base_time + i * 2.0
        )
        events.append(event)
        
        # Write to file
        with open(events_file, 'a') as f:
            f.write(json.dumps(event) + '\n')
    
    print(f"[File Transfer Sim] Generated {len(events)} file transfer events, saved to {events_file}")
    return events


if __name__ == "__main__":
    # Run simulation
    events = simulate_file_exfiltration(file_count=3, size_mb=100.0)
    print(f"Generated {len(events)} file transfer events")

