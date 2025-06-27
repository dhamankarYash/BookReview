#!/bin/bash

echo "=== Book Review Service Setup (No Docker) ==="
echo ""

# Step 1: Create project directory
echo "Step 1: Creating project directory..."
mkdir -p book-review-service
cd book-review-service

# Step 2: Create virtual environment
echo "Step 2: Creating Python virtual environment..."
python3 -m venv venv

# Step 3: Activate virtual environment
echo "Step 3: Activating virtual environment..."
source venv/bin/activate

# Step 4: Install dependencies
echo "Step 4: Installing Python dependencies..."
pip install --upgrade pip
pip install fastapi==0.104.1 uvicorn[standard]==0.24.0 sqlalchemy==2.0.23 redis==5.0.1 pytest==7.4.3 httpx==0.25.2 python-multipart==0.0.6 pydantic==2.5.0 alembic==1.12.1

# Step 5: Create requirements.txt
echo "Step 5: Creating requirements.txt..."
pip freeze > requirements.txt

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Copy your Python files to this directory"
echo "2. Run: alembic init alembic"
echo "3. Run: alembic revision --autogenerate -m 'Initial migration'"
echo "4. Run: alembic upgrade head"
echo "5. Start server: uvicorn main:app --reload"
