# Build and run the Docker container
Write-Host "Building and starting Vehicle Price Prediction services..." -ForegroundColor Green

# Create necessary directories
New-Item -ItemType Directory -Force -Path "logs"
New-Item -ItemType Directory -Force -Path "faiss_index"

# Build the Docker image
Write-Host "Building Docker image..." -ForegroundColor Yellow
docker-compose build

# Start all services
Write-Host "Starting services..." -ForegroundColor Yellow
docker-compose up -d

# Wait for services to be ready
Write-Host "Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check service status
Write-Host "Checking service status..." -ForegroundColor Yellow
docker-compose ps

# Show logs for the main application
Write-Host "Application logs:" -ForegroundColor Yellow
docker-compose logs app

Write-Host "Services are running!" -ForegroundColor Green
Write-Host "Access the application at: http://localhost" -ForegroundColor Cyan
Write-Host "Grafana dashboard at: http://localhost:3000 (admin/admin)" -ForegroundColor Cyan
Write-Host "Prometheus metrics at: http://localhost:9090" -ForegroundColor Cyan

Write-Host "To stop services: docker-compose down" -ForegroundColor White
Write-Host "To view logs: docker-compose logs -f" -ForegroundColor White
