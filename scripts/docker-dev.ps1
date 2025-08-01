# Development Docker setup script
Write-Host "Setting up development environment with Docker..." -ForegroundColor Green

# Create necessary directories
New-Item -ItemType Directory -Force -Path "logs"
New-Item -ItemType Directory -Force -Path "faiss_index"

# Copy environment file for development
if (!(Test-Path ".env")) {
    Copy-Item ".env.docker" ".env"
    Write-Host "Created .env file from template. Please update with your API keys." -ForegroundColor Yellow
}

# Build and start development services
Write-Host "Building development Docker image..." -ForegroundColor Yellow
docker-compose -f docker-compose.dev.yml build

Write-Host "Starting development services..." -ForegroundColor Yellow
docker-compose -f docker-compose.dev.yml up -d

# Wait for services to start
Write-Host "Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check service status
Write-Host "Development services status:" -ForegroundColor Yellow
docker-compose -f docker-compose.dev.yml ps

Write-Host "Development environment ready!" -ForegroundColor Green
Write-Host "Application: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Redis: localhost:6379" -ForegroundColor Cyan

Write-Host "To stop: docker-compose -f docker-compose.dev.yml down" -ForegroundColor White
Write-Host "To view logs: docker-compose -f docker-compose.dev.yml logs -f" -ForegroundColor White
