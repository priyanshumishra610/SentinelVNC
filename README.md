# SentinelVNC 🛡️

**AI-Driven Defense and Monitoring Platform for VNC Data Exfiltration**

SentinelVNC detects and contains data exfiltration attacks in VNC sessions through hybrid rule-based and ML detection, with blockchain-anchored forensic evidence.

---

## 🎯 Overview

SentinelVNC is a hackathon MVP that monitors VNC (Virtual Network Computing) sessions for:
- **Clipboard Abuse**: Large clipboard operations indicating data exfiltration
- **Screenshot Scraping**: Rapid screenshot capture patterns
- **File Exfiltration**: Unusual file transfer activities

The system uses a hybrid approach combining:
1. **Rule-based detection** (3 core rules with low false-positive rates)
2. **ML-based anomaly detection** (RandomForest with SHAP explainability)
3. **Blockchain anchoring** (Merkle tree-based forensic evidence)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+ (3.11 preferred, but 3.10+ works)
- Linux/macOS (tested on macOS, should work on Linux)
- 2GB+ RAM
- Internet connection (for initial package installation)

### Installation

```bash
# Clone or navigate to the repository
cd /path/to/SentinelVNC

# Create virtual environment
python3 -m venv venv  # or python3.11 if available

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
mkdir -p data/synthetic models logs forensic anchors
```

### Run Complete Demo

```bash
# Make script executable
chmod +x run_demo.sh

# Run the demo (trains model, simulates attacks, detects, anchors, launches dashboard)
./run_demo.sh
```

The script will:
1. Train the ML model (if not already trained)
2. Clear old simulation data
3. Generate synthetic attack events
4. Run the detector to identify threats
5. Create blockchain anchors from forensic evidence
6. Launch the Streamlit dashboard

---

## 📁 Project Structure

```
SentinelVNC/
├── attack_simulator.py      # Generates synthetic VNC attack events
├── detector.py               # Hybrid rule-based + ML detection engine
├── train_model.py            # ML model training with SHAP
├── streamlit_app.py          # Real-time monitoring dashboard
├── merkle_anchor.py          # Blockchain anchoring (Merkle tree)
├── run_demo.sh               # End-to-end demo orchestration
├── requirements.txt           # Python dependencies
├── README.md                 # This file
├── DEMO_SCRIPT.md            # Demo presentation script
├── SLIDES.md                 # 6-slide presentation outline
├── FAQ.md                    # FAQ for judges
├── DEVELOPMENT_PLAN.md       # Development plan
├── data/
│   └── synthetic/            # Generated attack events
├── models/                   # Trained ML models
├── logs/                     # Detection alerts
├── forensic/                 # Forensic JSON records
└── anchors/                  # Blockchain anchor files
```

---

## 🔧 Component Details

### 1. Attack Simulator (`attack_simulator.py`)

Generates synthetic VNC events to simulate attacks:

**Scenarios:**
- `normal`: Normal user activity
- `clipboard_abuse`: Large clipboard operations
- `screenshot_scraping`: Rapid screenshot capture
- `file_exfiltration`: Large file transfers
- `mixed`: Combination of all attacks

**Usage:**
```bash
python attack_simulator.py
```

**Output:** `data/synthetic/vnc_events.jsonl` (JSONL format, one event per line)

### 2. Detector (`detector.py`)

Hybrid detection engine with 3 core rules:

**Rule 1: Clipboard Size Threshold**
- Alerts if clipboard operation > 200KB
- Reason: Large clipboard operations indicate bulk data exfiltration

**Rule 2: Screenshot Burst**
- Alerts if 5+ screenshots within 10 seconds
- Reason: Rapid screenshot capture suggests scraping

**Rule 3: File Transfer**
- Alerts if file > 50MB OR 2+ large files within 30 seconds
- Reason: Unusual file transfer patterns

**ML Detection:**
- Uses trained RandomForest model
- Anomaly score threshold: 0.5
- Features: event type, sizes, temporal patterns, history

**Usage:**
```bash
python detector.py
```

**Output:**
- `logs/alerts.jsonl`: All detected alerts
- `forensic/*.json`: Forensic records for each alert

### 3. ML Training (`train_model.py`)

Trains a lightweight RandomForest classifier:

**Features:**
- Event type encoding (clipboard/screenshot/file_transfer)
- Size features (normalized)
- Temporal features (time of day)
- History features (recent activity counts)

**Explainability:**
- SHAP values for feature importance
- Feature importance rankings
- Saved to `models/shap_data.json`

**Usage:**
```bash
python train_model.py
```

**Output:**
- `models/detection_model.pkl`: Trained model
- `models/model_metadata.json`: Model metadata
- `models/shap_data.json`: SHAP explainability data

### 4. Streamlit Dashboard (`streamlit_app.py`)

Real-time monitoring dashboard with:
- Live alerts feed
- Detection analysis (charts and statistics)
- Forensic timeline
- Blockchain anchors viewer
- Containment button (simulated)

**Usage:**
```bash
streamlit run streamlit_app.py
```

**Access:** Dashboard opens at `http://localhost:8501`

### 5. Blockchain Anchoring (`merkle_anchor.py`)

Creates Merkle tree from forensic events:

**Process:**
1. Collects all forensic JSON files
2. Computes SHA-256 hash of each file
3. Builds Merkle tree
4. Generates root hash
5. Signs anchor with signature hash

**Usage:**
```bash
python merkle_anchor.py
```

**Output:** `anchors/*.json` (anchor metadata with Merkle root)

**Verification:**
```python
from merkle_anchor import ForensicAnchoring
anchorer = ForensicAnchoring()
anchorer.verify_anchor(Path("anchors/ANCHOR_123.json"))
```

---

## 🧪 Testing Individual Components

### Test Attack Simulator
```bash
python attack_simulator.py
# Check: data/synthetic/vnc_events.jsonl
```

### Test Detector
```bash
# First generate events
python attack_simulator.py

# Then run detector
python detector.py
# Check: logs/alerts.jsonl, forensic/*.json
```

### Test ML Training
```bash
python train_model.py
# Check: models/detection_model.pkl
```

### Test Anchoring
```bash
# First generate alerts (creates forensic files)
python attack_simulator.py
python detector.py

# Then create anchor
python merkle_anchor.py
# Check: anchors/*.json
```

---

## 📊 Demo Flow

1. **Setup** (30 seconds)
   - Show project structure
   - Explain hybrid detection approach

2. **Attack Simulation** (20 seconds)
   - Run `attack_simulator.py` with mixed scenario
   - Show generated events

3. **Detection** (30 seconds)
   - Run `detector.py`
   - Show alerts with explainable reasons
   - Highlight rule-based + ML detection

4. **Forensic Anchoring** (20 seconds)
   - Run `merkle_anchor.py`
   - Show Merkle root and verification

5. **Dashboard** (30 seconds)
   - Launch Streamlit dashboard
   - Show live alerts, analysis, anchors
   - Demonstrate containment button

**Total: ~2 minutes**

---

## 🔒 Security & Privacy

- **Simulated attacks only**: All attack patterns are synthetic and benign
- **No real VNC data**: System works with simulated events
- **Air-gapped compatible**: No cloud dependencies, runs entirely locally
- **Forensic integrity**: Merkle tree ensures evidence tamper-proofing

---

## 🛠️ Troubleshooting

### Issue: Model not found
**Solution:** Run `python train_model.py` first

### Issue: No alerts detected
**Solution:** Ensure events are generated: `python attack_simulator.py`

### Issue: Dashboard shows no data
**Solution:** Run the full demo: `./run_demo.sh`

### Issue: Import errors
**Solution:** Ensure virtual environment is activated and requirements installed

### Issue: Permission denied on run_demo.sh
**Solution:** `chmod +x run_demo.sh`

---

## 📈 Performance

- **Model training**: ~10-30 seconds (2000 samples)
- **Detection latency**: <100ms per event
- **Dashboard refresh**: 1-5 seconds (configurable)
- **Memory usage**: ~200-500MB

---

## 🎓 For Hackathon Judges

See:
- `DEMO_SCRIPT.md`: Step-by-step demo script
- `SLIDES.md`: 6-slide presentation outline
- `FAQ.md`: Answers to common questions

---

## 📝 License

This is a hackathon MVP. Use for demonstration purposes only.

---

## 👤 Author

Built for hackathon grand finale demo.

---

## 🙏 Acknowledgments

- scikit-learn for ML capabilities
- Streamlit for dashboard framework
- SHAP for explainability
