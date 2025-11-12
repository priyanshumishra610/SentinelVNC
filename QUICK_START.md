# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Python 3.10+
- Docker & Docker Compose (optional, for containerized deployment)

### Step 1: Clone and Setup

```bash
# Clone repository
git clone <repository-url>
cd SentinelVNC

# Copy environment file
cp .env.example .env

# Install dependencies
make install
# OR: pip install -r requirements.txt
```

### Step 2: Seed Data

```bash
# Create sample data and ML model
make seed
# OR: python scripts/seed_data.py
```

### Step 3: Start Services

#### Option A: Docker Compose (Recommended)

```bash
make up
# OR: cd infra && docker-compose up --build
```

#### Option B: Local Development

```bash
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload

# Terminal 2: Dashboard
cd dashboard
streamlit run streamlit_app.py

# Terminal 3: Proxy (optional)
python sentinelvnc_proxy.py --listen 0.0.0.0:5900 --server localhost:5901
```

### Step 4: Verify

1. **Backend API**: http://localhost:8000/docs
2. **Dashboard**: http://localhost:8501
3. **Health Check**: http://localhost:8000/health

### Step 5: Run Attack Simulation

```bash
# Run all attack scenarios
./attack_simulator/run_all_scenarios.sh

# Check alerts
curl http://localhost:8000/api/v1/alerts
```

## 📋 Common Commands

```bash
# Run tests
make test

# Check coverage
make coverage

# Lint code
make lint

# Stop services
make down

# Clean up
make clean
```

## 🎯 Next Steps

- See `docs/DEMO_SCRIPT.md` for full demonstration
- See `docs/SCENARIO_MATRIX.md` for attack scenarios
- See `docs/INSTALL.md` for detailed installation

## 🐛 Troubleshooting

**Port conflicts?** Edit `infra/docker-compose.yml` or `.env`

**Database errors?** Ensure PostgreSQL is running or use SQLite (default)

**Model not found?** Run `make seed` to create sample model

**Import errors?** Ensure virtual environment is activated: `source venv/bin/activate`
