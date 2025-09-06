# Vehicle Price Prediction - Docker Compose Startup Script (Windows)
Write-Host "🚀 Starting Vehicle Price Prediction with Ollama..." -ForegroundColor Green

# Check if Docker and Docker Compose are installed
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker is not installed. Please install Docker Desktop first." -ForegroundColor Red
    exit 1
}

if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker Compose is not installed. Please install Docker Compose first." -ForegroundColor Red
    exit 1
}

# Create necessary directories
Write-Host "📁 Creating required directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "data", "logs", "cache", "knowledge_base", "models" | Out-Null

# Pull latest images
Write-Host "📥 Pulling latest Docker images..." -ForegroundColor Yellow
docker-compose pull

# Start services
Write-Host "🦙 Starting Ollama and Redis services..." -ForegroundColor Yellow
docker-compose up -d ollama redis

# Wait for Ollama to be ready
Write-Host "⏳ Waiting for Ollama to be ready..." -ForegroundColor Yellow
for ($i = 1; $i -le 30; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Ollama is ready!" -ForegroundColor Green
            break
        }
    }
    catch {
        # Continue waiting
    }
    Write-Host "Waiting for Ollama... ($i/30)" -ForegroundColor Gray
    Start-Sleep -Seconds 2
}

# Pull Ollama models
Write-Host "📥 Downloading Ollama models..." -ForegroundColor Yellow
docker-compose up ollama-setup

# Start the main application
Write-Host "🚀 Starting main application..." -ForegroundColor Yellow
docker-compose up -d app

# Wait for application to be ready
Write-Host "⏳ Waiting for application to be ready..." -ForegroundColor Yellow
for ($i = 1; $i -le 20; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 3 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Application is ready!" -ForegroundColor Green
            break
        }
    }
    catch {
        # Continue waiting
    }
    Write-Host "Waiting for application... ($i/20)" -ForegroundColor Gray
    Start-Sleep -Seconds 3
}

# Show status
Write-Host ""
Write-Host "🎉 Vehicle Price Prediction is running!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Services:" -ForegroundColor Cyan
Write-Host "  - Application: http://localhost:8000" -ForegroundColor White
Write-Host "  - API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  - Health Check: http://localhost:8000/health" -ForegroundColor White
Write-Host "  - Ollama: http://localhost:11434" -ForegroundColor White
Write-Host "  - Redis: localhost:6379" -ForegroundColor White
Write-Host ""
Write-Host "🔍 Useful commands:" -ForegroundColor Cyan
Write-Host "  - View logs: docker-compose logs -f app" -ForegroundColor White
Write-Host "  - View all logs: docker-compose logs -f" -ForegroundColor White
Write-Host "  - Stop services: docker-compose down" -ForegroundColor White
Write-Host "  - Restart app: docker-compose restart app" -ForegroundColor White
Write-Host ""

# Show container status
docker-compose ps
