# Installation Guide - SentinelVNC v2

## Option 1: Docker Installation (Recommended)

### Install Docker Desktop for macOS

1. **Download Docker Desktop**
   - Visit: https://www.docker.com/products/docker-desktop/
   - Download Docker Desktop for Mac (Intel or Apple Silicon)
   - Install the `.dmg` file

2. **Start Docker Desktop**
   - Open Docker Desktop from Applications
   - Wait for Docker to start (whale icon in menu bar)

3. **Verify Installation**
   ```bash
   docker --version
   docker compose version
   ```

4. **Start SentinelVNC**
   ```bash
   cd /path/to/SentinelVNC
   cp .env.example .env
   # Edit .env if needed
   docker compose up -d
   ```

5. **Check Services**
   ```bash
   docker compose ps
   docker compose logs -f api
   ```

**Access:**
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Dashboard: http://localhost:8501

---

## Option 2: Local Development (Without Docker)

### Prerequisites

1. **Python 3.11+**
   ```bash
   python3 --version
   # Should be 3.11 or higher
   ```

2. **PostgreSQL**
   ```bash
   # Install via Homebrew
   brew install postgresql@15
   brew services start postgresql@15
   
   # Create database
   createdb sentinelvnc
   ```

3. **MongoDB**
   ```bash
   # Install via Homebrew
   brew tap mongodb/brew
   brew install mongodb-community@7.0
   brew services start mongodb-community@7.0
   ```

4. **Redis**
   ```bash
   # Install via Homebrew
   brew install redis
   brew services start redis
   ```

### Setup Steps

1. **Create Virtual Environment**
   ```bash
   cd /path/to/SentinelVNC
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install Dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

4. **Setup Databases**
   ```bash
   # PostgreSQL
   psql -U postgres -c "CREATE DATABASE sentinelvnc;"
   psql -U postgres -c "CREATE USER sentinel WITH PASSWORD 'sentinel';"
   psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE sentinelvnc TO sentinel;"
   
   # MongoDB (no setup needed, will create on first use)
   ```

5. **Run Database Migrations**
   ```bash
   # Create migrations (if needed)
   alembic revision --autogenerate -m "Initial migration"
   
   # Apply migrations
   alembic upgrade head
   ```

6. **Train ML Models**
   ```bash
   python train_model.py
   ```

7. **Start Services**

   **Terminal 1 - FastAPI Backend:**
   ```bash
   uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
   ```

   **Terminal 2 - Celery Worker:**
   ```bash
   celery -A backend.services.celery_tasks worker --loglevel=info
   ```

   **Terminal 3 - Streamlit Dashboard:**
   ```bash
   streamlit run streamlit_app.py --server.port 8501
   ```

8. **Access Services**
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Dashboard: http://localhost:8501

---

## Option 3: Minimal Setup (Testing Only)

For quick testing without databases:

1. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Existing v1 Components**
   ```bash
   # Train model
   python train_model.py
   
   # Simulate attacks
   python attack_simulator.py
   
   # Run detector
   python detector.py
   
   # View dashboard
   streamlit run streamlit_app.py
   ```

**Note:** This uses file-based storage (JSONL) instead of databases. Full v2 features require databases.

---

## Troubleshooting

### Docker Issues

**Issue: Docker not starting**
- Solution: Check Docker Desktop is running
- Verify: `docker ps` should work

**Issue: Port already in use**
- Solution: Stop conflicting services or change ports in `docker-compose.yml`

**Issue: Permission denied**
- Solution: Add user to docker group or use `sudo` (not recommended)

### Database Issues

**Issue: PostgreSQL connection failed**
- Solution: Check PostgreSQL is running: `brew services list`
- Verify credentials in `.env`

**Issue: MongoDB connection failed**
- Solution: Check MongoDB is running: `brew services list`
- Check logs: `tail -f /usr/local/var/log/mongodb/mongo.log`

**Issue: Redis connection failed**
- Solution: Check Redis is running: `redis-cli ping`
- Should return: `PONG`

### Python Issues

**Issue: Import errors**
- Solution: Ensure virtual environment is activated
- Reinstall: `pip install -r requirements.txt`

**Issue: Module not found**
- Solution: Check Python path includes project root
- Verify: `python -c "import backend"`

---

## Quick Start Script

Create `quick_start.sh`:

```bash
#!/bin/bash

# Check Docker
if command -v docker &> /dev/null; then
    echo "Using Docker..."
    docker compose up -d
    echo "Services starting..."
    sleep 10
    echo "API: http://localhost:8000"
    echo "Dashboard: http://localhost:8501"
else
    echo "Docker not found. Using local setup..."
    source venv/bin/activate
    uvicorn backend.api.main:app --reload &
    celery -A backend.services.celery_tasks worker --loglevel=info &
    streamlit run streamlit_app.py &
    echo "Services starting..."
fi
```

Make executable:
```bash
chmod +x quick_start.sh
./quick_start.sh
```

---

## Next Steps

After installation:

1. **Test API**
   ```bash
   curl http://localhost:8000/health
   ```

2. **View API Docs**
   - Open: http://localhost:8000/docs

3. **Create Admin User**
   - Use API endpoint: `POST /api/v1/auth/register`
   - Or create via Python script

4. **Run Demo**
   ```bash
   ./run_demo.sh
   ```

---

## Support

For issues:
1. Check logs: `docker compose logs` or service logs
2. Review [README_V2.md](README_V2.md)
3. Check [SECURITY.md](SECURITY.md) for configuration
4. Review API docs: http://localhost:8000/docs

