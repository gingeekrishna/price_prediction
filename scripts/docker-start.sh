#!/bin/bash

# Build and run the Docker container
echo "Building and starting Vehicle Price Prediction services..."

# Create necessary directories
mkdir -p logs
mkdir -p faiss_index

# Build the Docker image
echo "Building Docker image..."
docker-compose build

# Start all services
echo "Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 10

# Check service status
echo "Checking service status..."
docker-compose ps

# Show logs for the main application
echo "Application logs:"
docker-compose logs app

echo "Services are running!"
echo "Access the application at: http://localhost"
echo "Grafana dashboard at: http://localhost:3000 (admin/admin)"
echo "Prometheus metrics at: http://localhost:9090"

echo "To stop services: docker-compose down"
echo "To view logs: docker-compose logs -f"
