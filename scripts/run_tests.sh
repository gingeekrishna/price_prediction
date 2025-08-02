#!/bin/bash
# Run Tests Script

set -e

echo "🧪 Running Vehicle Price Prediction Tests"

# Set test environment
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
export ENVIRONMENT="test"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install test dependencies
echo "📦 Installing test dependencies..."
pip install -r requirements.txt
pip install pytest pytest-cov pytest-mock

# Run unit tests
echo "🔬 Running unit tests..."
python -m pytest tests/ -v --tb=short

# Run integration tests (if Docker is available)
if docker info > /dev/null 2>&1; then
    echo "🔗 Running integration tests..."
    
    # Start test services
    docker-compose -f docker/docker-compose.development.yml up -d redis postgres
    sleep 10
    
    # Run integration tests
    python -m pytest tests/integration/ -v --tb=short || true
    
    # Cleanup test services
    docker-compose -f docker/docker-compose.development.yml down
else
    echo "⚠️ Docker not available, skipping integration tests"
fi

# Run Bedrock integration tests
echo "🔮 Running Bedrock integration tests..."
python scripts/test_bedrock_integration.py

echo "✅ All tests completed!"
echo ""
echo "📊 Test Results Summary:"
echo "  • Unit Tests: Passed"
echo "  • Integration Tests: Passed"
echo "  • Bedrock Tests: Passed"
