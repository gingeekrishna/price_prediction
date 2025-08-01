#!/bin/bash

# Development Docker setup script
echo "Setting up development environment with Docker..."

# Create necessary directories
mkdir -p logs
mkdir -p faiss_index

# Copy environment file for development
if [ ! -f .env ]; then
    cp .env.docker .env
    echo "Created .env file from template. Please update with your API keys."
fi

# Build and start development services
echo "Building development Docker image..."
docker-compose -f docker-compose.dev.yml build

echo "Starting development services..."
docker-compose -f docker-compose.dev.yml up -d

# Wait for services to start
echo "Waiting for services to start..."
sleep 5

# Check service status
echo "Development services status:"
docker-compose -f docker-compose.dev.yml ps

echo "Development environment ready!"
echo "Application: http://localhost:8000"
echo "Redis: localhost:6379"

echo "To stop: docker-compose -f docker-compose.dev.yml down"
echo "To view logs: docker-compose -f docker-compose.dev.yml logs -f"
