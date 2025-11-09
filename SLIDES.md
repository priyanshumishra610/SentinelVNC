# SentinelVNC Presentation Slides (6 Slides)

---

## Slide 1: Title & Problem Statement

**Title:** SentinelVNC: AI-Driven Defense for VNC Data Exfiltration

**Subtitle:** Hybrid Detection + Blockchain-Anchored Forensics

**Content:**
- **Problem:** VNC sessions vulnerable to data exfiltration
  - Clipboard abuse (bulk data copying)
  - Screenshot scraping (rapid capture)
  - File exfiltration (unauthorized transfers)
- **Impact:** Sensitive data leaks, compliance violations, security breaches
- **Solution:** Real-time detection + containment + forensic evidence

**Visual:** VNC session diagram with attack vectors highlighted

---

## Slide 2: Architecture & Approach

**Title:** Hybrid Detection Architecture

**Content:**
- **Rule-Based Detection (3 Core Rules)**
  - Rule 1: Clipboard size threshold (>200KB)
  - Rule 2: Screenshot burst detection (5+ in 10s)
  - Rule 3: File transfer anomaly (large/rapid transfers)
- **ML-Based Detection**
  - RandomForest classifier
  - Features: event types, sizes, temporal patterns, history
  - Anomaly score threshold: 0.5
- **Explainability**
  - Human-readable reasons for every alert
  - SHAP values for ML feature importance

**Visual:** Architecture diagram showing rules + ML → alerts

---

## Slide 3: Detection Flow

**Title:** End-to-End Detection Pipeline

**Content:**
1. **Event Generation**
   - VNC events (clipboard, screenshots, file transfers)
   - Simulated attacks for testing
2. **Hybrid Detection**
   - Rule-based: Fast, low false positives
   - ML-based: Catches subtle patterns
   - Combined scoring
3. **Alert Generation**
   - Severity classification (high/medium)
   - Explainable reasons
   - Forensic JSON creation
4. **Blockchain Anchoring**
   - Merkle tree from forensic records
   - Signed root hash
   - Tamper-proof evidence

**Visual:** Flow diagram with numbered steps

---

## Slide 4: Key Features & Innovation

**Title:** What Makes SentinelVNC Unique

**Content:**
- **Hybrid Detection**
  - Best of both worlds: rules for obvious, ML for subtle
  - Low false-positive rate through careful threshold tuning
- **Explainable AI**
  - Every alert includes human-readable reasons
  - SHAP values show feature contributions
  - Not a black box - security teams can understand decisions
- **Blockchain-Anchored Forensics**
  - Merkle tree ensures evidence integrity
  - Verifiable, tamper-proof records
  - Lightweight (no full blockchain needed for MVP)
- **Real-Time Monitoring**
  - Streamlit dashboard for live alerts
  - Containment actions (disconnect, block IP)
  - Forensic timeline visualization

**Visual:** Feature icons or screenshots

---

## Slide 5: Demo Results

**Title:** Live Demo Results

**Content:**
- **Attack Simulation**
  - Mixed scenario: clipboard abuse + screenshot scraping + file exfiltration
  - Generated X events
- **Detection Results**
  - X alerts detected
  - Y high-severity, Z medium-severity
  - Detection methods: Rule-based (X), ML-based (Y), Both (Z)
- **Forensic Records**
  - X forensic JSON files created
  - All alerts anchored to Merkle root
- **Performance**
  - Detection latency: <100ms per event
  - Model accuracy: X% (from training)
  - False positive rate: <Y%

**Visual:** Dashboard screenshot or summary statistics

---

## Slide 6: Future Work & Conclusion

**Title:** Next Steps & Impact

**Content:**
- **Immediate Next Steps (1 week each)**
  1. Real VNC integration (hook into actual VNC sessions)
  2. Advanced ML models (deep learning for pattern recognition)
  3. Distributed anchoring (full blockchain integration)
- **Production Readiness**
  - Enterprise deployment considerations
  - Scalability improvements
  - Enhanced containment actions
- **Impact**
  - Protects sensitive data in remote access scenarios
  - Provides forensic evidence for compliance
  - Reduces false positives through hybrid approach
- **Conclusion**
  - Working MVP with end-to-end detection → containment → forensics
  - Explainable, verifiable, production-ready foundation

**Visual:** Roadmap or impact metrics

---

## Design Notes

- **Color Scheme:** Blue/red for security theme (blue = defense, red = threats)
- **Fonts:** Clear, readable (Arial or similar)
- **Visuals:** Use diagrams, screenshots, charts
- **Keep it Simple:** 6 slides = ~1 minute per slide (6 minutes total)
- **Practice:** Time yourself - should be 5-7 minutes for full presentation

---

## Alternative: Condensed 3-Slide Version (for 3-minute pitch)

**Slide 1:** Problem + Solution (combine slides 1 & 2)
**Slide 2:** Demo Results (slide 5)
**Slide 3:** Impact & Next Steps (slide 6)

