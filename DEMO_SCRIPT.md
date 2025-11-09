# SentinelVNC Demo Script (60-90 seconds)

## Pre-Demo Setup (Before Judges Arrive)
1. Ensure virtual environment is set up
2. Train model: `python train_model.py` (if not done)
3. Have terminal and browser ready
4. Clear old data: `rm -f data/synthetic/vnc_events.jsonl logs/alerts.jsonl forensic/*.json`

---

## Demo Script

### [0:00-0:10] Introduction & Problem Statement
**Speaker:**
> "Good morning! Today I'm presenting SentinelVNC - an AI-driven defense platform that detects and contains data exfiltration attacks in VNC sessions. VNC is widely used for remote access, but it's vulnerable to clipboard abuse, screenshot scraping, and file exfiltration. Our system uses hybrid rule-based and ML detection with blockchain-anchored forensics."

**Action:** Show project structure briefly

---

### [0:10-0:25] Attack Simulation
**Speaker:**
> "Let me demonstrate by simulating an attack. I'll generate a mixed attack scenario with clipboard abuse, screenshot scraping, and file exfiltration."

**Action:**
```bash
python attack_simulator.py
```

**Speaker (while running):**
> "The simulator generates synthetic VNC events - clipboard copies, screenshots, and file transfers. These events are saved in JSONL format for processing."

**Action:** Show a few lines of `data/synthetic/vnc_events.jsonl`

---

### [0:25-0:50] Detection & Explainability
**Speaker:**
> "Now let's run our hybrid detector. It combines three rule-based detection rules with an ML anomaly detection model."

**Action:**
```bash
python detector.py
```

**Speaker (while alerts appear):**
> "As you can see, we're detecting multiple threats:
> - Rule 1 triggered: Large clipboard operation detected - 500KB exceeds our 200KB threshold
> - Rule 2 triggered: Screenshot burst - 8 screenshots in 10 seconds
> - Rule 3 triggered: Large file transfer - 100MB file detected
> - ML model also flagged these as anomalies with high confidence scores"

**Action:** Show alert output, highlight the reasons

**Speaker:**
> "Every alert includes human-readable reasons. The ML model uses SHAP values for explainability, so we can see which features contributed to the detection."

**Action:** Show forensic JSON file with reasons

---

### [0:50-1:05] Blockchain Anchoring
**Speaker:**
> "For forensic integrity, we anchor all alerts to a Merkle tree. This creates tamper-proof evidence that can be verified later."

**Action:**
```bash
python merkle_anchor.py
```

**Speaker:**
> "The system creates a Merkle root hash from all forensic records. This root is signed and stored. Any tampering with the forensic files would invalidate the root hash."

**Action:** Show anchor JSON with Merkle root

---

### [1:05-1:30] Dashboard & Containment
**Speaker:**
> "Finally, let's see the real-time dashboard that security teams would use."

**Action:**
```bash
streamlit run streamlit_app.py
```

**Speaker (while dashboard loads):**
> "The dashboard shows:
> - Live alerts with severity levels
> - Detection analysis with charts
> - Forensic timeline
> - Blockchain anchors
> - A containment button for immediate threat response"

**Action:** 
- Navigate through dashboard tabs
- Show an alert with reasons
- Click "Contain Threat" button
- Show blockchain anchors tab

**Speaker:**
> "The containment action is simulated here, but in production it would disconnect the VNC session, block the IP, and trigger incident response."

---

### [1:30-1:35] Closing
**Speaker:**
> "In summary, SentinelVNC provides:
> 1. Hybrid detection with low false positives
> 2. Explainable AI with human-readable reasons
> 3. Blockchain-anchored forensics for evidence integrity
> 4. Real-time monitoring and containment
> 
> The entire system runs locally, requires no cloud, and is air-gapped compatible. Thank you!"

---

## Backup Plan (If Something Fails)

**If model training fails:**
- Use pre-trained model if available
- Explain: "We use a pre-trained model for the demo"

**If dashboard doesn't load:**
- Show JSON files directly
- Explain: "The dashboard provides a visual interface, but all data is available in structured JSON format"

**If detection shows no alerts:**
- Manually check events file
- Re-run simulator with more aggressive scenario
- Explain: "The system is tuned for low false positives, but we can adjust thresholds"

---

## Key Points to Emphasize

1. **Hybrid Approach**: Rules catch obvious patterns, ML catches subtle anomalies
2. **Explainability**: Every alert has clear reasons (not a black box)
3. **Forensic Integrity**: Blockchain anchoring ensures evidence can't be tampered
4. **Production-Ready MVP**: Complete end-to-end flow, not just a proof of concept
5. **Air-Gapped**: No cloud dependencies, runs entirely locally

---

## Timing Notes

- **Fast version**: 60 seconds (skip some dashboard details)
- **Full version**: 90 seconds (show all features)
- **Practice**: Run through 2-3 times to get timing right

