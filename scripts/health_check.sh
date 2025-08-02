#!/bin/bash
# Health Check Script

set -e

echo "🔍 Running health checks..."

# Check API health
echo "Checking API health..."
API_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health || echo "000")
if [ "$API_RESPONSE" = "200" ]; then
    echo "✅ API is healthy"
else
    echo "❌ API health check failed (HTTP $API_RESPONSE)"
    exit 1
fi

# Check Redis connection
echo "Checking Redis connection..."
REDIS_RESPONSE=$(docker exec vehicle_price_redis redis-cli ping 2>/dev/null || echo "FAIL")
if [ "$REDIS_RESPONSE" = "PONG" ]; then
    echo "✅ Redis is healthy"
else
    echo "❌ Redis health check failed"
    exit 1
fi

# Check PostgreSQL connection
echo "Checking PostgreSQL connection..."
PG_RESPONSE=$(docker exec vehicle_price_postgres pg_isready -U vehicleuser -d vehicledb 2>/dev/null || echo "FAIL")
if echo "$PG_RESPONSE" | grep -q "accepting connections"; then
    echo "✅ PostgreSQL is healthy"
else
    echo "❌ PostgreSQL health check failed"
    exit 1
fi

# Check Ollama (if in development)
if docker ps | grep -q vehicle_price_ollama; then
    echo "Checking Ollama connection..."
    OLLAMA_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:11434/api/version || echo "000")
    if [ "$OLLAMA_RESPONSE" = "200" ]; then
        echo "✅ Ollama is healthy"
    else
        echo "❌ Ollama health check failed (HTTP $OLLAMA_RESPONSE)"
    fi
fi

# Check Bedrock (if configured)
if [ ! -z "$AWS_ACCESS_KEY_ID" ]; then
    echo "Checking Bedrock connection..."
    BEDROCK_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/bedrock/status || echo "000")
    if [ "$BEDROCK_RESPONSE" = "200" ]; then
        echo "✅ Bedrock is configured and accessible"
    else
        echo "⚠️ Bedrock connection check failed (may be using mock mode)"
    fi
fi

echo "🎉 All health checks completed!"
