#!/bin/bash

echo "=== Starting Book Review Service ==="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if database exists, if not create it
if [ ! -f "book_reviews.db" ]; then
    echo "Setting up database..."
    alembic upgrade head
    echo "Seeding database with sample data..."
    python seed_data.py
fi

# Check Redis (optional)
echo "Checking Redis..."
if command -v redis-server &> /dev/null; then
    if ! pgrep -x "redis-server" > /dev/null; then
        echo "Starting Redis server..."
        redis-server --daemonize yes
    else
        echo "Redis is already running"
    fi
else
    echo "⚠️  Redis not installed. Service will run without caching."
fi

echo ""
echo "🚀 Starting FastAPI server..."
echo "📖 API Documentation: http://localhost:8000/docs"
echo "🔍 Alternative Docs: http://localhost:8000/redoc"
echo "❤️  Health Check: http://localhost:8000/health"
echo ""

uvicorn main:app --reload --host 0.0.0.0 --port 8000
