#!/bin/bash

echo "🚀 SentinelVNC v2 - Local Development Setup"
echo "=============================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.11+"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Check virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check databases
echo "🔍 Checking databases..."

# PostgreSQL
if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL not found. Install with: brew install postgresql@15"
else
    echo "✅ PostgreSQL found"
fi

# MongoDB
if ! command -v mongosh &> /dev/null && ! command -v mongo &> /dev/null; then
    echo "⚠️  MongoDB not found. Install with: brew install mongodb-community@7.0"
else
    echo "✅ MongoDB found"
fi

# Redis
if ! command -v redis-cli &> /dev/null; then
    echo "⚠️  Redis not found. Install with: brew install redis"
else
    echo "✅ Redis found"
fi

echo ""
echo "📝 Next steps:"
echo "1. Start PostgreSQL: brew services start postgresql@15"
echo "2. Start MongoDB: brew services start mongodb-community@7.0"
echo "3. Start Redis: brew services start redis"
echo "4. Run migrations: alembic upgrade head"
echo "5. Train models: python train_model.py"
echo "6. Start API: uvicorn backend.api.main:app --reload"
echo "7. Start Celery: celery -A backend.services.celery_tasks worker --loglevel=info"
echo "8. Start Dashboard: streamlit run streamlit_app.py"
echo ""
echo "Or use the existing v1 components for testing:"
echo "  python attack_simulator.py"
echo "  python detector.py"
echo "  streamlit run streamlit_app.py"
