# SentinelVNC Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Setup Environment (2 minutes)

```bash
# Navigate to project
cd /Users/priyanshumishra/Documents/SentinelVNC

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 2: Train ML Model (1 minute)

```bash
python train_model.py
```

This will:
- Generate synthetic training dataset
- Train RandomForest classifier
- Save model to `models/detection_model.pkl`
- Generate SHAP explainability data

### Step 3: Run Complete Demo (2 minutes)

```bash
./run_demo.sh
```

This will:
1. Generate attack events
2. Run detector
3. Create blockchain anchors
4. Launch Streamlit dashboard

**Or run manually:**

```bash
# Generate attacks
python attack_simulator.py

# Detect threats
python detector.py

# Create anchors
python merkle_anchor.py

# Launch dashboard
streamlit run streamlit_app.py
```

---

## 📋 File Checklist

✅ **Core Files:**
- [x] `attack_simulator.py` - Generates synthetic VNC events
- [x] `detector.py` - Hybrid detection engine
- [x] `train_model.py` - ML model training
- [x] `streamlit_app.py` - Real-time dashboard
- [x] `merkle_anchor.py` - Blockchain anchoring

✅ **Configuration:**
- [x] `requirements.txt` - Python dependencies
- [x] `run_demo.sh` - Demo orchestration script

✅ **Documentation:**
- [x] `README.md` - Comprehensive documentation
- [x] `DEVELOPMENT_PLAN.md` - 7-step development plan
- [x] `DEMO_SCRIPT.md` - 60-90 second demo script
- [x] `SLIDES.md` - 6-slide presentation outline
- [x] `FAQ.md` - FAQ for judges
- [x] `OPTIONAL_IMPROVEMENTS.md` - 3 optional improvements

---

## 🧪 Test Individual Components

### Test Attack Simulator
```bash
python attack_simulator.py
# Check: data/synthetic/vnc_events.jsonl
```

### Test Detector
```bash
python attack_simulator.py  # Generate events first
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
python attack_simulator.py  # Generate events
python detector.py          # Generate alerts
python merkle_anchor.py     # Create anchor
# Check: anchors/*.json
```

### Test Dashboard
```bash
streamlit run streamlit_app.py
# Open: http://localhost:8501
```

---

## 📊 Expected Output

After running the demo, you should see:

**Files Created:**
- `data/synthetic/vnc_events.jsonl` - Generated events
- `logs/alerts.jsonl` - Detected alerts
- `forensic/*.json` - Forensic records
- `anchors/*.json` - Blockchain anchors
- `models/detection_model.pkl` - Trained model

**Dashboard:**
- Live alerts feed
- Detection analysis charts
- Forensic timeline
- Blockchain anchors viewer

---

## ⚠️ Troubleshooting

### Issue: Module not found
**Solution:** Ensure virtual environment is activated and requirements installed

### Issue: Model not found
**Solution:** Run `python train_model.py` first

### Issue: No alerts detected
**Solution:** Ensure events are generated: `python attack_simulator.py`

### Issue: Permission denied on run_demo.sh
**Solution:** `chmod +x run_demo.sh`

### Issue: Dashboard shows no data
**Solution:** Run full demo: `./run_demo.sh`

---

## 🎯 Next Steps

1. **Review Documentation:**
   - Read `README.md` for full details
   - Review `DEMO_SCRIPT.md` for presentation
   - Check `FAQ.md` for judge questions

2. **Practice Demo:**
   - Run through demo script 2-3 times
   - Time yourself (aim for 60-90 seconds)
   - Prepare answers for FAQ

3. **Optional Improvements:**
   - Review `OPTIONAL_IMPROVEMENTS.md`
   - Consider implementing #1 (Real VNC Integration) if time permits

---

## 📞 Support

If you encounter issues:
1. Check `README.md` troubleshooting section
2. Verify all dependencies are installed
3. Ensure Python 3.11 is being used
4. Check that all directories are created

---

## ✅ Verification Checklist

Before presenting:
- [ ] Virtual environment created and activated
- [ ] All dependencies installed
- [ ] ML model trained (`models/detection_model.pkl` exists)
- [ ] Demo script runs successfully
- [ ] Dashboard launches and shows data
- [ ] Demo script practiced (60-90 seconds)
- [ ] FAQ reviewed
- [ ] Slides prepared

---

**Good luck with your hackathon! 🚀**

