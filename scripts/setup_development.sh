#!/bin/bash
# Setup Development Environment

set -e

echo "🚀 Setting up Vehicle Price Prediction - Development Environment"

# Create necessary directories
mkdir -p logs data faiss_index

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

echo "📦 Pulling required Docker images..."
docker-compose -f docker/docker-compose.development.yml pull

echo "🔧 Building development containers..."
docker-compose -f docker/docker-compose.development.yml build

echo "🚀 Starting development environment..."
docker-compose -f docker/docker-compose.development.yml up -d

echo "⏳ Waiting for services to start..."
sleep 30

echo "🧠 Setting up Ollama models..."
docker exec vehicle_price_ollama_dev ollama pull llama2:7b
docker exec vehicle_price_ollama_dev ollama pull mistral:7b

echo "✅ Development environment setup complete!"
echo ""
echo "🌐 Services available at:"
echo "  • API: http://localhost:8000"
echo "  • Ollama: http://localhost:11434"
echo "  • Redis: localhost:6379"
echo "  • PostgreSQL: localhost:5432"
echo ""
echo "🧪 Run tests with: ./scripts/run_tests.sh"
echo "📊 View logs with: docker-compose -f docker/docker-compose.development.yml logs -f"
