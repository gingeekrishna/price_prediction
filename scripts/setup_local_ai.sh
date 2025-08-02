#!/bin/bash
# setup_local_ai.sh - Setup local AI environment

echo "🚀 Setting up Local AI Environment for Vehicle Price Prediction"

# Pull Ollama Docker image
echo "📦 Pulling Ollama Docker image..."
docker pull ollama/ollama:latest

# Start Ollama container
echo "🐳 Starting Ollama container..."
docker run -d \
  --name ollama \
  -p 11434:11434 \
  -v ollama_data:/root/.ollama \
  ollama/ollama:latest

# Wait for Ollama to start
echo "⏳ Waiting for Ollama to start..."
sleep 10

# Pull recommended models
echo "🧠 Pulling recommended AI models..."
docker exec ollama ollama pull llama2:7b
docker exec ollama ollama pull codellama:7b
docker exec ollama ollama pull mistral:7b

echo "✅ Local AI setup complete!"
echo ""
echo "🎯 Available Models:"
docker exec ollama ollama list

echo ""
echo "🌐 Ollama API available at: http://localhost:11434"
echo "🚗 Start your Vehicle Price API with local AI support!"
echo ""
echo "💡 To use: Set OLLAMA_AVAILABLE=true in your environment"
