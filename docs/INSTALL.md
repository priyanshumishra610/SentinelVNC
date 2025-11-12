# Installation Guide

## Prerequisites

- Python 3.10 or higher
- Docker and Docker Compose (for containerized deployment)
- PostgreSQL (optional, SQLite used by default for local dev)
- Redis (optional, for Celery tasks)

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd SentinelVNC
```

### 2. Set Up Environment

```bash
# Copy environment file
cp .env.example .env

# Edit .env with your configuration
nano .env  # or use your preferred editor
```

### 3. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Initialize Database

```bash
# Run migrations (if using Alembic)
# Or create tables directly
python -c "from backend.app.models import Base, engine; Base.metadata.create_all(bind=engine)"
```

### 5. Seed Sample Data

```bash
python scripts/seed_data.py
```

### 6. Train ML Model (Optional)

```bash
python train_model.py
```

### 7. Start Services

#### Option A: Docker Compose (Recommended)

```bash
cd infra
docker-compose up --build
```

#### Option B: Local Development

```bash
# Terminal 1: Start backend
cd backend
uvicorn app.main:app --reload

# Terminal 2: Start dashboard
cd dashboard
streamlit run streamlit_app.py

# Terminal 3: Start proxy (optional)
python sentinelvnc_proxy.py --listen 0.0.0.0:5900 --server localhost:5901
```

## Verification

1. **Backend API**: http://localhost:8000/docs
2. **Dashboard**: http://localhost:8501
3. **Health Check**: http://localhost:8000/health

## Troubleshooting

### Database Connection Issues

- Ensure PostgreSQL is running (if using PostgreSQL)
- Check DATABASE_URL in .env
- For SQLite, ensure write permissions

### Port Conflicts

- Change ports in docker-compose.yml or .env
- Backend: 8000
- Dashboard: 8501
- Proxy: 5900

### ML Model Not Found

- Run `python train_model.py` to create model
- Or use seed_data.py which creates a sample model

## Next Steps

- See `docs/DEMO_SCRIPT.md` for demo instructions
- See `docs/SCENARIO_MATRIX.md` for attack scenarios
- Run `./attack_simulator/run_all_scenarios.sh` to test detection

