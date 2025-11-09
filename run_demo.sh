#!/bin/bash
# SentinelVNC Demo Orchestration Script
# Runs the complete end-to-end demo

set -e

echo "=========================================="
echo "SentinelVNC Demo Script"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Detect Python version (prefer python3.11, fallback to python3)
PYTHON_CMD="python3.11"
if ! command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3"
    echo -e "${YELLOW}python3.11 not found, using python3${NC}"
fi

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo -e "${BLUE}Using Python ${PYTHON_VERSION}${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    $PYTHON_CMD -m venv venv
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

# Install requirements if needed
if [ ! -f "venv/.requirements_installed" ]; then
    echo -e "${BLUE}Installing requirements...${NC}"
    pip install --upgrade pip
    pip install -r requirements.txt
    touch venv/.requirements_installed
fi

# Create necessary directories
echo -e "${BLUE}Creating directories...${NC}"
mkdir -p data/synthetic models logs forensic anchors

# Step 1: Train ML model (if not exists)
if [ ! -f "models/detection_model.pkl" ]; then
    echo -e "${GREEN}Step 1: Training ML model...${NC}"
    python train_model.py
    echo ""
else
    echo -e "${GREEN}Step 1: ML model already exists, skipping training${NC}"
    echo ""
fi

# Step 2: Clear old data
echo -e "${GREEN}Step 2: Clearing old simulation data...${NC}"
rm -f data/synthetic/vnc_events.jsonl
rm -f logs/alerts.jsonl
rm -f forensic/*.json
rm -f anchors/*.json
echo ""

# Step 3: Run attack simulator
echo -e "${GREEN}Step 3: Running attack simulator (mixed scenario)...${NC}"
python attack_simulator.py
echo ""

# Wait a moment for files to be written
sleep 2

# Step 4: Run detector
echo -e "${GREEN}Step 4: Running detector...${NC}"
python detector.py
echo ""

# Step 5: Create blockchain anchor
echo -e "${GREEN}Step 5: Creating blockchain anchor...${NC}"
python merkle_anchor.py
echo ""

# Step 6: Summary
echo -e "${GREEN}Step 6: Demo Summary${NC}"
echo "=========================================="
echo "Events generated: $(wc -l < data/synthetic/vnc_events.jsonl 2>/dev/null || echo 0)"
echo "Alerts detected: $(wc -l < logs/alerts.jsonl 2>/dev/null || echo 0)"
echo "Forensic records: $(ls -1 forensic/*.json 2>/dev/null | wc -l || echo 0)"
echo "Anchors created: $(ls -1 anchors/*.json 2>/dev/null | wc -l || echo 0)"
echo ""

# Step 7: Launch dashboard
echo -e "${GREEN}Step 7: Launching Streamlit dashboard...${NC}"
echo -e "${YELLOW}Dashboard will open in your browser.${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop the dashboard.${NC}"
echo ""
streamlit run streamlit_app.py

