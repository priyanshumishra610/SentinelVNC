# Attack Scenario Matrix

Six scenarios demonstrating detection and defense capabilities.

## Scenario 1: Clipboard Abuse

**Description:** Large clipboard operations indicating bulk data exfiltration

**Simulation:**
```bash
python attack_simulator/clipboard_sim.py
```

**Pattern:**
- 5 clipboard copies
- Each 500KB
- Rapid succession (0.5s intervals)

**Expected Detection:**
- ✅ Rule 1: Clipboard size threshold (>200KB)
- ✅ ML: High anomaly score (large size + rapid pattern)
- **Severity:** HIGH
- **Action:** Contain recommended

**Defense:**
- Proxy detects client->server burst
- Alert sent to backend
- Forensic bundle created
- Containment available

---

## Scenario 2: Screenshot Scraping

**Description:** Rapid screenshot capture suggesting screen scraping

**Simulation:**
```bash
python attack_simulator/screenshot_burst_sim.py
```

**Pattern:**
- 10 screenshots
- 0.5 second intervals
- Within 10 second window

**Expected Detection:**
- ✅ Rule 2: Screenshot burst (5+ in 10s)
- ✅ ML: Temporal pattern anomaly
- **Severity:** MEDIUM
- **Action:** Monitor and alert

**Defense:**
- Proxy detects rapid screenshot pattern
- Alert with burst count
- Forensic evidence captured
- Optional containment

---

## Scenario 3: File Transfer Exfiltration

**Description:** Large file transfers indicating data exfiltration

**Simulation:**
```bash
python attack_simulator/file_transfer_sim.py
```

**Pattern:**
- 3 files
- Each 100MB
- 2 second intervals

**Expected Detection:**
- ✅ Rule 3: Large file transfer (>50MB)
- ✅ ML: High anomaly score
- **Severity:** HIGH
- **Action:** Immediate containment

**Defense:**
- Proxy detects sustained high rate
- Alert with file metadata
- Forensic bundle with file hashes
- Automatic containment (if enabled)

---

## Scenario 4: Mixed Attack Pattern

**Description:** Combination of all attack types

**Simulation:**
```bash
./attack_simulator/run_all_scenarios.sh
```

**Pattern:**
- Normal activity (20s)
- Clipboard abuse (3 events, 300KB)
- Screenshot burst (8 screenshots)
- File transfers (2 files, 50MB)

**Expected Detection:**
- ✅ Multiple rule triggers
- ✅ ML: Very high anomaly score
- **Severity:** CRITICAL
- **Action:** Immediate containment

**Defense:**
- Multiple alerts generated
- Comprehensive forensic bundle
- Automatic containment
- Full audit trail

---

## Scenario 5: Normal Activity (Baseline)

**Description:** Legitimate VNC usage patterns

**Simulation:**
```python
# From attack_simulator.py
simulator = AttackSimulator()
simulator.simulate_normal_activity(duration_seconds=60)
```

**Pattern:**
- Small clipboard operations (<50KB)
- Occasional screenshots
- Normal file operations

**Expected Detection:**
- ❌ No rule triggers
- ❌ ML: Low anomaly score (<0.3)
- **Severity:** N/A
- **Action:** No action needed

**Defense:**
- Baseline established
- Low false positive rate
- System learns normal patterns

---

## Scenario 6: Stealthy Exfiltration

**Description:** Slow, low-volume exfiltration attempt

**Simulation:**
```python
# Custom: Small but frequent transfers
for i in range(20):
    generate_clipboard_event(size_kb=150, timestamp=time.time() + i * 60)
```

**Pattern:**
- 20 clipboard copies
- Each 150KB (below threshold)
- 1 minute intervals
- Total: 3MB over 20 minutes

**Expected Detection:**
- ⚠️ Rule 1: May not trigger (below 200KB threshold)
- ✅ ML: Detects pattern anomaly (frequency + total volume)
- **Severity:** MEDIUM
- **Action:** Investigate

**Defense:**
- ML catches pattern ML misses
- Historical context analysis
- Cumulative volume detection
- Alert for investigation

---

## Detection Summary

| Scenario | Rule-Based | ML-Based | Severity | Contain |
|----------|-----------|----------|----------|---------|
| Clipboard Abuse | ✅ | ✅ | HIGH | Yes |
| Screenshot Scraping | ✅ | ✅ | MEDIUM | Optional |
| File Transfer | ✅ | ✅ | HIGH | Yes |
| Mixed Attack | ✅✅✅ | ✅ | CRITICAL | Yes |
| Normal Activity | ❌ | ❌ | N/A | No |
| Stealthy Exfil | ⚠️ | ✅ | MEDIUM | Investigate |

## Key Takeaways

1. **Hybrid Detection**: Rules catch obvious, ML catches subtle
2. **Low False Positives**: Normal activity passes through
3. **Comprehensive Coverage**: Multiple attack vectors detected
4. **Forensic Integrity**: All alerts anchored with Merkle trees
5. **Rapid Response**: Real-time alerts and containment

## Running All Scenarios

```bash
# Run complete test suite
./attack_simulator/run_all_scenarios.sh

# Check results
python detector.py
cat logs/alerts.jsonl | jq .

# View in dashboard
streamlit run dashboard/streamlit_app.py
```

