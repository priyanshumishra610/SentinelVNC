#!/bin/bash
# Orchestrate all attack simulation scenarios
# This script runs each scenario sequentially and shows expected detection

set -e

echo "=========================================="
echo "SentinelVNC Attack Simulation Scenarios"
echo "=========================================="
echo ""
echo "NOTE: All simulations are benign and safe for testing."
echo "No actual data exfiltration occurs."
echo ""

# Create output directory
mkdir -p data/synthetic/screenshots

# Clear previous events (optional)
read -p "Clear previous simulation data? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -f data/synthetic/vnc_events.jsonl
    echo "Cleared previous events"
fi

echo ""
echo "Running scenarios..."
echo ""

# Scenario 1: Clipboard Abuse
echo "=== Scenario 1: Clipboard Abuse ==="
echo "Expected: Detection of large clipboard operations (>200KB)"
python3 attack_simulator/clipboard_sim.py
echo "✓ Clipboard abuse simulation complete"
echo ""

# Scenario 2: Screenshot Burst
echo "=== Scenario 2: Screenshot Burst ==="
echo "Expected: Detection of rapid screenshot capture (5+ in 10s)"
python3 attack_simulator/screenshot_burst_sim.py
echo "✓ Screenshot burst simulation complete"
echo ""

# Scenario 3: File Transfer
echo "=== Scenario 3: File Transfer Exfiltration ==="
echo "Expected: Detection of large file transfers (>50MB)"
python3 attack_simulator/file_transfer_sim.py
echo "✓ File transfer simulation complete"
echo ""

echo "=========================================="
echo "All scenarios complete!"
echo "=========================================="
echo ""
echo "Events saved to: data/synthetic/vnc_events.jsonl"
echo ""
echo "Next steps:"
echo "1. Run the detector: python detector.py"
echo "2. Check alerts: logs/alerts.jsonl"
echo "3. View dashboard: streamlit run dashboard/streamlit_app.py"
echo ""

