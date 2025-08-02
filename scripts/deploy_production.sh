#!/bin/bash
# Production Deployment Script

set -e

echo "🚀 Deploying Vehicle Price Prediction - Production Environment"

# Check environment variables
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "❌ AWS credentials not found. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY"
    exit 1
fi

echo "📦 Pulling production images..."
docker-compose -f docker/docker-compose.production.yml pull

echo "🔧 Building production containers..."
docker-compose -f docker/docker-compose.production.yml build

echo "🚀 Starting production services..."
docker-compose -f docker/docker-compose.production.yml up -d

echo "⏳ Waiting for services to start..."
sleep 45

echo "🧪 Running health checks..."
./scripts/health_check.sh

echo "✅ Production deployment complete!"
echo ""
echo "🌐 Service endpoints:"
echo "  • API: https://api.vehicleprice.com"
echo "  • Health: https://api.vehicleprice.com/health"
echo "  • Metrics: https://api.vehicleprice.com/metrics"
