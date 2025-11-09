# SentinelVNC Development Plan

## 7-Step Development Plan

### Step 1: Environment Setup & Dependencies
- Create Python 3.11 virtual environment
- Install all required packages (scikit-learn, streamlit, Pillow, web3.py, etc.)
- Verify installation and Python version

### Step 2: Core Infrastructure
- Create directory structure (data/, models/, logs/, forensic/)
- Implement attack_simulator.py (generates synthetic VNC events)
- Implement detector.py (rule-based + ML scoring engine)
- Create event queue/storage mechanism

### Step 3: Machine Learning Pipeline
- Create train_model.py with synthetic dataset generation
- Train lightweight ML model (RandomForest or small neural network)
- Integrate SHAP for explainability
- Save model artifacts and feature importance

### Step 4: Detection & Containment Logic
- Implement 3 core rules (clipboard-size, screenshot-burst, file-transfer)
- Integrate ML model scoring
- Create forensic JSON generation
- Implement containment action (simulated)

### Step 5: Blockchain Anchoring POC
- Implement merkle_anchor.py (simpler than Ganache for MVP)
- Create Merkle tree from forensic events
- Generate signed root hash
- Store anchor metadata

### Step 6: Streamlit Dashboard
- Build streamlit_app.py with live alert feed
- Display detection reasons (SHAP values + rules)
- Add containment button
- Show forensic timeline and blockchain anchors

### Step 7: Integration & Testing
- Create run_demo.sh orchestration script
- Test end-to-end flow (simulate → detect → contain → anchor)
- Generate demo script and slides
- Create FAQ document

---

## Setup Commands

```bash
# Navigate to project directory
cd /Users/priyanshumishra/Documents/SentinelVNC

# Create Python 3.11 virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt

# Verify installation
python --version  # Should show Python 3.11.x
pip list | grep -E "(streamlit|scikit-learn|Pillow|web3|shap)"

# Create necessary directories
mkdir -p data/synthetic models logs forensic anchors

# Run the demo
chmod +x run_demo.sh
./run_demo.sh
```


