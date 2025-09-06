#!/bin/bash

# Vehicle Price Prediction - Docker Compose Startup Script
echo "🚀 Starting Vehicle Price Prediction with Ollama..."

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating required directories..."
mkdir -p data logs cache knowledge_base models

# Set permissions
chmod 755 data logs cache knowledge_base models

# Pull latest images
echo "📥 Pulling latest Docker images..."
docker-compose pull

# Start services
echo "🦙 Starting Ollama and application services..."
docker-compose up -d ollama redis

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:11434/api/tags > /dev/null; then
        echo "✅ Ollama is ready!"
        break
    fi
    echo "Waiting for Ollama... ($i/30)"
    sleep 2
done

# Pull Ollama models
echo "📥 Downloading Ollama models..."
docker-compose up ollama-setup

# Start the main application
echo "🚀 Starting main application..."
docker-compose up -d app

# Wait for application to be ready
echo "⏳ Waiting for application to be ready..."
for i in {1..20}; do
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ Application is ready!"
        break
    fi
    echo "Waiting for application... ($i/20)"
    sleep 3
done

# Show status
echo ""
echo "🎉 Vehicle Price Prediction is running!"
echo ""
echo "📊 Services:"
echo "  - Application: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - Health Check: http://localhost:8000/health"
echo "  - Ollama: http://localhost:11434"
echo "  - Redis: localhost:6379"
echo ""
echo "🔍 Useful commands:"
echo "  - View logs: docker-compose logs -f app"
echo "  - View all logs: docker-compose logs -f"
echo "  - Stop services: docker-compose down"
echo "  - Restart app: docker-compose restart app"
echo ""

# Show container status
docker-compose ps
