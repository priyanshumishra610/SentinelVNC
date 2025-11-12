# Presentation Slides

6-slide presentation outline for SentinelVNC.

## Slide 1: Problem Statement

**Title:** VNC Data Exfiltration: A Growing Threat

**Content:**
- VNC (Virtual Network Computing) widely used for remote access
- Vulnerable to data exfiltration attacks:
  - Clipboard abuse (copying sensitive data)
  - Screenshot scraping (capturing screen content)
  - File transfer exfiltration (bulk data theft)
- Current solutions: Limited detection, no real-time response
- **Need:** Proactive detection and containment

**Visual:** Diagram showing VNC client → server with exfiltration vectors

---

## Slide 2: Solution Overview

**Title:** SentinelVNC: AI-Driven Security Layer

**Content:**
- **Transparent Proxy**: Sits between VNC client and server
- **Hybrid Detection**: Rule-based + ML anomaly detection
- **Real-time Alerts**: Immediate notification of threats
- **Forensic Anchoring**: Blockchain-anchored evidence (Merkle trees)
- **Containment**: Kill-switch capability to stop attacks

**Visual:** Architecture diagram (Client → Proxy → Server, with detection engine)

---

## Slide 3: Detection Engine

**Title:** Hybrid Detection: Rules + ML

**Content:**
- **Rule-Based (3 Core Rules):**
  1. Clipboard threshold (>200KB)
  2. Screenshot burst (5+ in 10s)
  3. File transfer size (>50MB)
- **ML-Based:**
  - RandomForest classifier
  - Anomaly scoring
  - SHAP explainability
- **Benefits:**
  - Low false positives
  - Catches stealthy attacks
  - Explainable decisions

**Visual:** Flowchart showing detection pipeline

---

## Slide 4: Forensic Integrity

**Title:** Tamper-Proof Evidence with Merkle Trees

**Content:**
- **Merkle Tree**: Cryptographic hash tree
- **Forensic Bundles**: All alerts anchored
- **Blockchain Integration**: Stub for demo (fake TX IDs)
- **Verification**: Proof of integrity
- **Use Cases**: Legal evidence, audit trails, compliance

**Visual:** Merkle tree diagram with root hash and blockchain anchor

---

## Slide 5: Demo Results

**Title:** Live Demonstration

**Content:**
- **Attack Simulation**: 3 scenarios (clipboard, screenshots, files)
- **Detection Results**: All attacks detected
- **Dashboard**: Real-time monitoring
- **Containment**: Successful session termination
- **Forensics**: Merkle roots and blockchain TXs generated

**Visual:** Screenshots of dashboard showing alerts and charts

---

## Slide 6: Impact & Next Steps

**Title:** Production-Ready Security Solution

**Content:**
- **Impact:**
  - Real-time threat detection
  - Zero-day attack prevention
  - Forensic evidence for compliance
  - Scalable architecture
- **Next Steps:**
  - Real blockchain integration
  - Enhanced ML models
  - Multi-tenant support
  - Cloud deployment

**Visual:** Roadmap timeline

---

## Presentation Tips

1. **Slide 1**: Start with real-world impact (data breaches)
2. **Slide 2**: Show architecture clearly
3. **Slide 3**: Emphasize hybrid approach (best of both worlds)
4. **Slide 4**: Highlight security/forensics (compliance angle)
5. **Slide 5**: **LIVE DEMO** - Most important slide
6. **Slide 6**: End with vision and roadmap

## Demo Flow (During Slide 5)

1. Show dashboard (empty state)
2. Run attack simulator
3. Show alerts appearing in real-time
4. Demonstrate containment action
5. Show forensic data and Merkle roots
6. Verify integrity

**Total Time: 10-12 minutes** (2 min per slide + 2 min demo)

