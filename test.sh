#!/bin/bash

echo "=== Running Tests ==="
echo ""

# Activate virtual environment
source venv/bin/activate

# Run tests
echo "Running unit tests..."
pytest test_main.py -v

echo ""
echo "Running all tests with coverage..."
pytest --cov=. --cov-report=term-missing

echo ""
echo "✅ Tests completed!"
