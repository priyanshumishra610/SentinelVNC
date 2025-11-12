# Demo Script

Step-by-step demonstration of SentinelVNC capabilities.

## Prerequisites

- All services running (backend, dashboard, proxy)
- Attack simulator ready
- ML model trained

## Demo Flow (5-10 minutes)

### 1. Setup (30 seconds)

**Show:**
- Project structure
- Explain: VNC proxy sits between client and server
- Explain: Hybrid detection (rules + ML)
- Explain: Forensic anchoring with Merkle trees

**Commands:**
```bash
# Show structure
tree -L 2 -I '__pycache__|*.pyc|venv'

# Show services
docker-compose ps  # or show running processes
```

### 2. Attack Simulation (1 minute)

**Demonstrate:** Simulate data exfiltration attacks

**Commands:**
```bash
# Run all scenarios
./attack_simulator/run_all_scenarios.sh

# Or run individually
python attack_simulator/clipboard_sim.py
python attack_simulator/screenshot_burst_sim.py
python attack_simulator/file_transfer_sim.py
```

**Expected Output:**
- Events generated in `data/synthetic/vnc_events.jsonl`
- Screenshots created in `data/synthetic/screenshots/`

**Explain:**
- These are benign simulations
- No actual data exfiltration
- Safe for testing

### 3. Detection (1-2 minutes)

**Demonstrate:** Detection engine identifies threats

**Commands:**
```bash
# Run detector
python detector.py

# Or if using backend API
curl http://localhost:8000/api/v1/alerts
```

**Expected Output:**
- Alerts in `logs/alerts.jsonl`
- Forensic JSON files in `forensic/`
- Console output showing detected threats

**Explain:**
- Rule-based detection (3 core rules)
- ML-based detection (anomaly scoring)
- Hybrid approach reduces false positives

### 4. Forensic Anchoring (1 minute)

**Demonstrate:** Create blockchain-anchored forensic evidence

**Commands:**
```bash
# Create Merkle anchor
python merkle_anchor.py

# Verify anchor
python -c "from merkle_anchor import ForensicAnchoring; a = ForensicAnchoring(); print(a.list_anchors())"
```

**Expected Output:**
- Anchor file in `anchors/`
- Merkle root hash
- Fake blockchain transaction ID

**Explain:**
- Merkle tree ensures integrity
- Tamper-proof evidence
- Blockchain anchoring (stub for demo)

### 5. Dashboard (2-3 minutes)

**Demonstrate:** Real-time monitoring and containment

**Commands:**
```bash
# Open dashboard
open http://localhost:8501
# Or: streamlit run dashboard/streamlit_app.py
```

**Show:**
1. **Live Alerts Tab**
   - Recent alerts
   - Severity levels
   - Detection reasons
   - ML scores

2. **Detection Analysis Tab**
   - Charts: methods distribution, severity, timeline
   - ML score histogram
   - Top heuristics

3. **Forensic Data Tab**
   - Forensic hashes
   - Blockchain transaction IDs
   - Alert details

4. **Containment Action**
   - Click "Contain" button on an alert
   - Show backend response
   - Explain: In production, this would close VNC connection

### 6. Containment (1 minute)

**Demonstrate:** Manual containment via API

**Commands:**
```bash
# Get session ID from alert
SESSION_ID="session_001"

# Contain session
curl -X POST http://localhost:8000/api/v1/contain \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"$SESSION_ID\"}"
```

**Expected Output:**
- Success response
- Alert marked as contained
- Dashboard updates

**Explain:**
- Kill-switch capability
- Immediate threat mitigation
- Audit trail

### 7. Verification (30 seconds)

**Demonstrate:** Verify forensic integrity

**Commands:**
```bash
# Verify anchor
python -c "
from merkle_anchor import ForensicAnchoring
a = ForensicAnchoring()
anchors = a.list_anchors()
if anchors:
    a.verify_anchor(a.anchors_dir / f\"{anchors[-1]['anchor_id']}.json\")
"
```

**Expected Output:**
- Verification success message
- Merkle root matches

## Key Points to Emphasize

1. **Hybrid Detection**: Rules + ML = Low false positives
2. **Forensic Integrity**: Merkle trees ensure tamper-proof evidence
3. **Real-time Response**: Immediate alerts and containment
4. **Explainability**: SHAP values show why alerts triggered
5. **Scalability**: Docker Compose for easy deployment

## Troubleshooting

- **No alerts**: Ensure events are generated and detector is running
- **Dashboard empty**: Check backend API is accessible
- **Model errors**: Run `python train_model.py` or use seed_data.py
- **Port conflicts**: Adjust ports in docker-compose.yml

## Time Breakdown

- Setup: 30s
- Simulation: 1m
- Detection: 1-2m
- Anchoring: 1m
- Dashboard: 2-3m
- Containment: 1m
- Verification: 30s

**Total: ~7-10 minutes**

