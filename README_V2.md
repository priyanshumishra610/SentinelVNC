# SentinelVNC v2 🛡️

**Government-Grade Real-Time Cybersecurity AI System**

SentinelVNC v2 is a production-ready, government-grade cybersecurity AI system for real-time VNC data exfiltration detection and monitoring. It combines rule-based detection, machine learning, and deep learning with blockchain-anchored forensic evidence.

---

## 🎯 Overview

SentinelVNC v2 provides:

- **Hybrid Detection**: Rules + ML (RandomForest) + DL (LSTM/Autoencoder)
- **Real-Time Processing**: FastAPI backend with Celery workers
- **Secure Authentication**: JWT with RBAC and 2FA (TOTP)
- **Production Database**: PostgreSQL + MongoDB
- **Real-Time Dashboard**: Streamlit with WebSocket updates
- **Blockchain Anchoring**: Merkle tree-based forensic evidence
- **ELK Stack**: Centralized logging and monitoring
- **Docker Deployment**: Full microservices architecture
- **CI/CD Pipeline**: GitHub Actions with automated testing

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development)
- 8GB+ RAM recommended
- Internet connection (for initial setup)

### Docker Deployment (Recommended)

```bash
# Clone repository
git clone <repository-url>
cd SentinelVNC

# Copy environment file
cp .env.example .env
# Edit .env with your settings

# Start all services
docker-compose up -d

# Check services
docker-compose ps

# View logs
docker-compose logs -f api
```

**Services:**
- API: http://localhost:8000
- Dashboard: http://localhost:8501
- API Docs: http://localhost:8000/docs
- Kibana: http://localhost:5601

### Local Development

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup databases (PostgreSQL and MongoDB must be running)
# Update .env with database credentials

# Run database migrations
alembic upgrade head

# Train ML models
python train_model.py

# Start API server
uvicorn backend.api.main:app --reload

# Start Celery worker (in separate terminal)
celery -A backend.services.celery_tasks worker --loglevel=info

# Start Streamlit dashboard (in separate terminal)
streamlit run streamlit_app.py
```

---

## 📁 Architecture

```
SentinelVNC/
├── backend/
│   ├── api/              # FastAPI application
│   │   ├── main.py       # FastAPI app
│   │   └── routes/       # API routes
│   ├── auth/             # Authentication & authorization
│   │   ├── jwt.py        # JWT token management
│   │   ├── totp.py       # 2FA (TOTP)
│   │   └── dependencies.py # Auth dependencies
│   ├── models/           # Database models
│   │   ├── database.py   # DB connections
│   │   ├── user.py       # User models
│   │   └── alert.py      # Alert models
│   ├── services/         # Business logic
│   │   ├── detection.py  # Hybrid detection service
│   │   └── celery_tasks.py # Celery tasks
│   └── config.py         # Configuration
├── frontend/
│   └── dashboard/        # Streamlit dashboard
├── services/
│   └── blockchain/       # Blockchain anchoring
├── docker-compose.yml    # Docker Compose setup
├── Dockerfile.*          # Dockerfiles
├── requirements.txt      # Python dependencies
└── .github/
    └── workflows/
        └── ci.yml        # CI/CD pipeline
```

---

## 🔧 Components

### 1. FastAPI Backend (`backend/api/`)

RESTful API with:
- JWT authentication
- Role-based access control (Admin, Analyst, Read-only)
- 2FA support (TOTP)
- WebSocket for real-time alerts
- OpenAPI documentation

**Endpoints:**
- `/api/v1/auth/*` - Authentication
- `/api/v1/users/*` - User management
- `/api/v1/alerts/*` - Alert management
- `/api/v1/detection/*` - Detection processing
- `/api/v1/ws/*` - WebSocket endpoints

### 2. Detection Service (`backend/services/detection.py`)

Hybrid detection engine:
- **Rule-Based**: 3 core rules (clipboard, screenshot, file transfer)
- **ML-Based**: RandomForest classifier with SHAP explainability
- **DL-Based**: LSTM/Autoencoder for behavioral anomaly detection
- **Ensemble**: Voting mechanism for final decision

### 3. Celery Workers (`backend/services/celery_tasks.py`)

Asynchronous task processing:
- Event detection processing
- Model retraining (weekly)
- Log archival (90-day retention)
- Alert broadcasting

### 4. Database Models

**PostgreSQL:**
- Users, roles, authentication
- Alerts, audit logs
- Refresh tokens

**MongoDB:**
- Raw event logs
- Forensic evidence
- Semi-structured data

### 5. Streamlit Dashboard (`frontend/dashboard/`)

Real-time monitoring dashboard:
- Live alert feed (WebSocket)
- Detection analysis (charts)
- User management (Admin)
- Blockchain anchors viewer
- System health metrics

### 6. Blockchain Anchoring (`services/blockchain/`)

Merkle tree-based forensic evidence:
- SHA-256 hashing
- Tamper-proof verification
- Evidence export

---

## 🔐 Security

### Authentication
- JWT tokens (access + refresh)
- bcrypt password hashing
- 2FA with TOTP (Google Authenticator)
- Account lockout after failed attempts

### Authorization
- Role-based access control (RBAC)
- Admin, Analyst, Read-only roles
- Endpoint-level permissions

### Encryption
- Data in transit: TLS/HTTPS
- Data at rest: AES-256
- Database: Encrypted connections

### Security Features
- Rate limiting
- Input validation
- SQL injection prevention (ORM)
- XSS protection
- CSRF protection
- Security headers

See [SECURITY.md](SECURITY.md) for detailed security documentation.

---

## 📊 API Usage

### Authentication

```python
import requests

# Login
response = requests.post("http://localhost:8000/api/v1/auth/login", json={
    "username": "admin",
    "password": "password",
    "totp_code": "123456"  # If 2FA enabled
})

token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Get current user
user = requests.get("http://localhost:8000/api/v1/auth/me", headers=headers)

# Process event
event = requests.post("http://localhost:8000/api/v1/detection/event", 
    headers=headers,
    json={
        "event_type": "clipboard_copy",
        "data": {"size_kb": 500}
    }
)
```

### WebSocket

```python
import asyncio
import websockets
import json

async def listen_alerts(token):
    uri = f"ws://localhost:8000/api/v1/ws/alerts?token={token}"
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            alert = json.loads(message)
            print(f"Alert: {alert}")

asyncio.run(listen_alerts("your-token"))
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=backend --cov-report=html

# Specific test file
pytest tests/test_detector.py

# Security scan
bandit -r backend/
safety check
```

**Coverage Target:** 90%+

---

## 🐳 Docker Commands

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down

# Clean volumes
docker-compose down -v
```

---

## 📈 Monitoring

### ELK Stack
- **Elasticsearch**: http://localhost:9200
- **Kibana**: http://localhost:5601

### Metrics
- API response times
- Detection latency
- Queue depth (Celery)
- Database connections
- System resources

### Alerts
- Email notifications (SMTP)
- Slack webhooks
- Custom integrations

---

## 🔄 CI/CD

GitHub Actions pipeline:
1. **Test**: Run pytest with coverage (>90%)
2. **Security**: Bandit + Safety scans
3. **Docker**: Build and push images to GHCR
4. **Deploy**: Auto-deploy to staging

See `.github/workflows/ci.yml` for details.

---

## 📝 Configuration

Environment variables (`.env`):

```bash
# Security
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key

# Databases
POSTGRES_HOST=localhost
POSTGRES_USER=sentinel
POSTGRES_PASSWORD=sentinel
POSTGRES_DB=sentinelvnc

MONGODB_HOST=localhost
MONGODB_USER=sentinel
MONGODB_PASSWORD=sentinel
MONGODB_DB=sentinelvnc_logs

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=sentinel

# Detection
ML_THRESHOLD=0.5
DL_THRESHOLD=0.5
```

See `.env.example` for all options.

---

## 🛠️ Development

### Makefile Commands

```bash
make install      # Install dependencies
make test         # Run tests
make lint         # Run linting
make security     # Security scans
make docker-up   # Start Docker services
make migrate      # Run database migrations
make train        # Train ML models
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## 📚 Documentation

- [SECURITY.md](SECURITY.md) - Security documentation
- [API Documentation](http://localhost:8000/docs) - OpenAPI/Swagger docs
- [FAQ.md](FAQ.md) - Frequently asked questions
- [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md) - Development roadmap

---

## 🚨 Troubleshooting

### Issue: Database connection failed
**Solution:** Ensure PostgreSQL/MongoDB are running and credentials are correct in `.env`

### Issue: Celery worker not processing tasks
**Solution:** Check Redis connection and worker logs: `docker-compose logs worker`

### Issue: 2FA not working
**Solution:** Ensure system time is synchronized (TOTP is time-based)

### Issue: WebSocket connection failed
**Solution:** Check token validity and WebSocket endpoint URL

---

## 📄 License

This is a government-grade cybersecurity system. Use for authorized purposes only.

---

## 👥 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Ensure coverage >90%
5. Submit pull request

---

## 🙏 Acknowledgments

- FastAPI for the web framework
- scikit-learn for ML capabilities
- TensorFlow for deep learning
- Streamlit for dashboard
- Docker for containerization

---

**Last Updated:** 2024-01-XX  
**Version:** 2.0.0

