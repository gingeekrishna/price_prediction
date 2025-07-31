# Ollama Integration Guide

## Overview

This guide covers integrating Ollama with the Vehicle Price Prediction system to enable local LLM capabilities for enhanced explanations, insights, and natural language interactions.

## What is Ollama?

Ollama is a tool that allows you to run large language models locally on your machine. It provides:
- Local LLM inference without API calls
- Privacy-focused AI interactions
- Support for various open-source models
- Easy model management and switching

## Installation

### Windows Installation

1. **Download Ollama:**
   - Visit: https://ollama.ai/download
   - Download the Windows installer
   - Run the installer and follow the setup wizard

2. **Verify Installation:**
   ```powershell
   ollama --version
   ```

### Alternative Installation Methods

**Using PowerShell (Windows):**
```powershell
# Download and install Ollama
Invoke-WebRequest -Uri "https://ollama.ai/install.sh" -OutFile "install-ollama.ps1"
.\install-ollama.ps1
```

**Using Package Managers:**
```bash
# macOS with Homebrew
brew install ollama

# Linux (Ubuntu/Debian)
curl -fsSL https://ollama.ai/install.sh | sh
```

## Recommended Models for Vehicle Price Prediction

### 1. General Purpose Models

**Llama 3.1 (8B) - Recommended for most users:**
```bash
ollama pull llama3.1:8b
```

**Llama 3.1 (70B) - For advanced users with powerful hardware:**
```bash
ollama pull llama3.1:70b
```

**Mistral 7B - Lightweight alternative:**
```bash
ollama pull mistral:7b
```

### 2. Code-Specialized Models

**CodeLlama (13B) - For code-related explanations:**
```bash
ollama pull codellama:13b
```

**Deepseek Coder - For technical documentation:**
```bash
ollama pull deepseek-coder:6.7b
```

### 3. Lightweight Models for Resource-Constrained Systems

**Phi-3 Mini - Very lightweight (3.8B parameters):**
```bash
ollama pull phi3:mini
```

**Gemma 2B - Google's lightweight model:**
```bash
ollama pull gemma:2b
```

## Model Recommendations by Use Case

| Use Case | Recommended Model | RAM Requirement | Speed |
|----------|-------------------|-----------------|-------|
| Quick explanations | Phi-3 Mini | 4GB | Fast |
| General purpose | Llama 3.1 8B | 8GB | Medium |
| Detailed analysis | Llama 3.1 70B | 40GB+ | Slow |
| Code explanations | CodeLlama 13B | 16GB | Medium |
| Production use | Mistral 7B | 8GB | Fast |

## System Requirements

### Minimum Requirements
- **RAM**: 8GB (for 7B models)
- **Storage**: 4GB per model
- **CPU**: Modern multi-core processor
- **GPU**: Optional (NVIDIA/AMD for acceleration)

### Recommended Requirements
- **RAM**: 16GB+ 
- **Storage**: 50GB+ free space
- **CPU**: 8+ cores
- **GPU**: NVIDIA RTX 3060+ or AMD equivalent

## Integration with Vehicle Price Prediction

### 1. Ollama Agent Implementation

Create a new file: `src/agents/ollama_agent.py`

```python
"""
Ollama Agent for Local LLM Integration

Provides natural language explanations and insights using local Ollama models.
"""

import requests
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class OllamaAgent:
    """
    Agent for interacting with local Ollama LLM models.
    
    Provides enhanced explanations, insights, and natural language
    processing capabilities for vehicle price predictions.
    """
    
    def __init__(self, 
                 model_name: str = "llama3.1:8b",
                 ollama_host: str = "http://localhost:11434",
                 timeout: int = 30):
        """
        Initialize Ollama Agent.
        
        Args:
            model_name: Name of the Ollama model to use
            ollama_host: Ollama server host URL
            timeout: Request timeout in seconds
        """
        self.model_name = model_name
        self.ollama_host = ollama_host
        self.timeout = timeout
        self.api_url = f"{ollama_host}/api"
        
        # Verify Ollama is running and model is available
        self._verify_setup()
        
    def _verify_setup(self) -> bool:
        """Verify Ollama is running and model is available."""
        try:
            # Check if Ollama is running
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=5)
            if response.status_code != 200:
                raise ConnectionError("Ollama server not responding")
            
            # Check if model is available
            models = response.json().get("models", [])
            model_names = [model["name"] for model in models]
            
            if self.model_name not in model_names:
                logger.warning(f"Model {self.model_name} not found. Available models: {model_names}")
                # Auto-pull the model if not available
                self._pull_model()
            
            logger.info(f"Ollama agent initialized with model: {self.model_name}")
            return True
            
        except Exception as e:
            logger.error(f"Ollama setup verification failed: {str(e)}")
            raise ConnectionError(f"Cannot connect to Ollama: {str(e)}")
    
    def _pull_model(self) -> None:
        """Pull the specified model if not available."""
        try:
            logger.info(f"Pulling model: {self.model_name}")
            response = requests.post(
                f"{self.api_url}/pull",
                json={"name": self.model_name},
                timeout=300  # 5 minutes timeout for model download
            )
            
            if response.status_code == 200:
                logger.info(f"Model {self.model_name} pulled successfully")
            else:
                logger.error(f"Failed to pull model: {response.text}")
                
        except Exception as e:
            logger.error(f"Error pulling model: {str(e)}")
    
    def generate_explanation(self, 
                           vehicle_data: Dict[str, Any], 
                           market_data: Dict[str, Any], 
                           predicted_price: float) -> str:
        """
        Generate detailed explanation using Ollama LLM.
        
        Args:
            vehicle_data: Vehicle information
            market_data: Market conditions
            predicted_price: Predicted price
            
        Returns:
            str: Detailed explanation from LLM
        """
        prompt = f"""
        As an automotive expert, explain this vehicle price prediction:
        
        Vehicle Details:
        - Age: {vehicle_data.get('vehicle_age')} years
        - Mileage: {vehicle_data.get('mileage')} km
        - Brand: {vehicle_data.get('brand', 'Unknown')}
        - Model: {vehicle_data.get('model', 'Unknown')}
        
        Market Conditions:
        - Market Index: {market_data.get('market_index')}
        - Fuel Price: ${market_data.get('fuel_price')}
        
        Predicted Price: ${predicted_price:,.2f}
        
        Please provide:
        1. Why this price is reasonable given the vehicle's characteristics
        2. How market conditions affected the prediction
        3. Factors that could increase or decrease the value
        4. Buying/selling recommendations
        
        Keep the explanation clear, professional, and under 200 words.
        """
        
        return self._query_ollama(prompt)
    
    def generate_insights(self, predicted_price: float, explanation: str) -> str:
        """
        Generate actionable insights using Ollama LLM.
        
        Args:
            predicted_price: Predicted vehicle price
            explanation: Previous explanation
            
        Returns:
            str: Actionable insights
        """
        prompt = f"""
        Based on this vehicle price prediction of ${predicted_price:,.2f} and the following analysis:
        
        {explanation}
        
        Provide 3-5 specific, actionable insights for:
        1. Buyers: What to look for, negotiate, or consider
        2. Sellers: How to maximize value or timing considerations
        3. Market context: Current trends affecting this price range
        
        Format as a numbered list, keep each point concise and actionable.
        """
        
        return self._query_ollama(prompt)
    
    def natural_language_query(self, query: str, context: Dict[str, Any]) -> str:
        """
        Handle natural language queries about vehicle pricing.
        
        Args:
            query: User's natural language question
            context: Context including vehicle data, predictions, etc.
            
        Returns:
            str: Natural language response
        """
        prompt = f"""
        You are an automotive pricing expert. Answer this question about vehicle pricing:
        
        Question: {query}
        
        Context:
        {json.dumps(context, indent=2)}
        
        Provide a helpful, accurate response based on the available data.
        If you need more information, clearly state what additional details would be helpful.
        """
        
        return self._query_ollama(prompt)
    
    def _query_ollama(self, prompt: str) -> str:
        """
        Send query to Ollama and return response.
        
        Args:
            prompt: Text prompt for the LLM
            
        Returns:
            str: LLM response
        """
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 500
                }
            }
            
            response = requests.post(
                f"{self.api_url}/generate",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return "Sorry, I couldn't generate a response at this time."
                
        except Exception as e:
            logger.error(f"Error querying Ollama: {str(e)}")
            return f"Error generating response: {str(e)}"
    
    def list_available_models(self) -> List[str]:
        """
        List all available Ollama models.
        
        Returns:
            List[str]: List of available model names
        """
        try:
            response = requests.get(f"{self.api_url}/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [model["name"] for model in models]
            return []
        except Exception as e:
            logger.error(f"Error listing models: {str(e)}")
            return []
    
    def switch_model(self, new_model: str) -> bool:
        """
        Switch to a different Ollama model.
        
        Args:
            new_model: Name of the new model to use
            
        Returns:
            bool: True if switch was successful
        """
        try:
            available_models = self.list_available_models()
            if new_model in available_models:
                self.model_name = new_model
                logger.info(f"Switched to model: {new_model}")
                return True
            else:
                logger.warning(f"Model {new_model} not available. Available: {available_models}")
                return False
        except Exception as e:
            logger.error(f"Error switching model: {str(e)}")
            return False


# Example usage
if __name__ == "__main__":
    # Initialize Ollama agent
    ollama = OllamaAgent()
    
    # Example vehicle data
    vehicle_data = {"vehicle_age": 3, "mileage": 45000, "brand": "Toyota", "model": "Camry"}
    market_data = {"market_index": 1125.0, "fuel_price": 3.80}
    predicted_price = 22500.0
    
    # Generate explanation
    explanation = ollama.generate_explanation(vehicle_data, market_data, predicted_price)
    print("Explanation:", explanation)
    
    # Generate insights
    insights = ollama.generate_insights(predicted_price, explanation)
    print("\\nInsights:", insights)
```

### 2. Integration with Existing Agents

Update `src/agents/explainer_agent.py` to include Ollama:

```python
# Add to existing ExplainerAgentRAG class
def __init__(self, use_ollama: bool = True):
    # Existing initialization code...
    
    if use_ollama:
        try:
            from .ollama_agent import OllamaAgent
            self.ollama_agent = OllamaAgent()
            self.use_ollama = True
        except Exception as e:
            logger.warning(f"Ollama not available, falling back to standard explanations: {e}")
            self.use_ollama = False
    else:
        self.use_ollama = False

def explain(self, input_data: dict, predicted_price: float) -> str:
    """Enhanced explanation with Ollama integration."""
    # Get standard explanation first
    standard_explanation = self._get_standard_explanation(input_data, predicted_price)
    
    # Enhance with Ollama if available
    if self.use_ollama and hasattr(self, 'ollama_agent'):
        try:
            vehicle_data = {
                'vehicle_age': input_data.get('vehicle_age'),
                'mileage': input_data.get('mileage')
            }
            market_data = {
                'market_index': input_data.get('market_index'),
                'fuel_price': input_data.get('fuel_price')
            }
            
            ollama_explanation = self.ollama_agent.generate_explanation(
                vehicle_data, market_data, predicted_price
            )
            return f"{standard_explanation}\\n\\n--- Enhanced Analysis ---\\n{ollama_explanation}"
        except Exception as e:
            logger.error(f"Ollama explanation failed: {e}")
    
    return standard_explanation
```

## API Integration

### Add Ollama Endpoint to FastAPI

Update `src/api.py`:

```python
from src.agents.ollama_agent import OllamaAgent

# Initialize Ollama agent (optional)
try:
    ollama_agent = OllamaAgent()
    OLLAMA_AVAILABLE = True
except Exception as e:
    logger.warning(f"Ollama not available: {e}")
    OLLAMA_AVAILABLE = False

@app.post("/predict_with_ollama")
async def predict_with_ollama(request: Request, payload: dict, response: Response):
    """Enhanced prediction with Ollama-powered explanations."""
    # ... existing prediction code ...
    
    if OLLAMA_AVAILABLE:
        try:
            # Generate enhanced explanation
            enhanced_explanation = ollama_agent.generate_explanation(
                vehicle_data, market_data, predicted_price
            )
            
            # Generate insights
            insights = ollama_agent.generate_insights(predicted_price, enhanced_explanation)
            
            return {
                "predicted_price": predicted_price,
                "explanation": enhanced_explanation,
                "insights": insights,
                "recommendation": recommendation,
                "market_data": market_data,
                "ollama_enhanced": True
            }
        except Exception as e:
            logger.error(f"Ollama enhancement failed: {e}")
    
    # Fallback to standard prediction
    return await predict(request, payload, response)

@app.get("/ollama/models")
async def list_ollama_models():
    """List available Ollama models."""
    if OLLAMA_AVAILABLE:
        models = ollama_agent.list_available_models()
        return {"models": models, "current": ollama_agent.model_name}
    return {"error": "Ollama not available"}

@app.post("/ollama/switch_model")
async def switch_ollama_model(model_name: str):
    """Switch Ollama model."""
    if OLLAMA_AVAILABLE:
        success = ollama_agent.switch_model(model_name)
        return {"success": success, "current_model": ollama_agent.model_name}
    return {"error": "Ollama not available"}
```

## Configuration

### Environment Variables

Create or update `.env` file:

```env
# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
OLLAMA_TIMEOUT=30
OLLAMA_ENABLED=true

# Model preferences by use case
OLLAMA_EXPLANATION_MODEL=llama3.1:8b
OLLAMA_INSIGHTS_MODEL=mistral:7b
OLLAMA_CHAT_MODEL=phi3:mini
```

### Configuration File

Create `ollama_config.json`:

```json
{
  "ollama": {
    "host": "http://localhost:11434",
    "default_model": "llama3.1:8b",
    "timeout": 30,
    "enabled": true,
    "models": {
      "explanation": "llama3.1:8b",
      "insights": "mistral:7b",
      "chat": "phi3:mini",
      "code": "codellama:13b"
    },
    "generation_options": {
      "temperature": 0.7,
      "top_p": 0.9,
      "max_tokens": 500
    }
  }
}
```

## Running the System

### 1. Start Ollama Service

```bash
# Start Ollama service
ollama serve

# In another terminal, pull required models
ollama pull llama3.1:8b
ollama pull mistral:7b
ollama pull phi3:mini
```

### 2. Start Vehicle Price Prediction Server

```bash
# Start the enhanced server
python run_server.py
```

### 3. Test Ollama Integration

```bash
# Test basic Ollama connection
curl http://localhost:11434/api/tags

# Test enhanced prediction endpoint
curl -X POST "http://127.0.0.1:8080/predict_with_ollama" \
     -H "Content-Type: application/json" \
     -d '{"vehicle_age": 3, "mileage": 45000}'
```

## Frontend Integration

### Update Frontend for Ollama Features

Add to `frontend/index.html`:

```javascript
// Add Ollama-enhanced prediction option
async function predictWithOllama() {
    const response = await fetch(`${this.apiUrl}/predict_with_ollama`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache'
        },
        body: JSON.stringify(vehicleData)
    });
    
    const result = await response.json();
    
    if (result.ollama_enhanced) {
        // Display enhanced explanation and insights
        displayEnhancedResult(result);
    } else {
        // Fallback to standard display
        showResult(result.predicted_price);
    }
}

function displayEnhancedResult(result) {
    // Create enhanced result display with Ollama insights
    const resultHTML = `
        <div class="ollama-enhanced-result">
            <h3>🤖 AI-Enhanced Prediction: $${result.predicted_price.toLocaleString()}</h3>
            <div class="explanation-section">
                <h4>📊 Detailed Analysis</h4>
                <p>${result.explanation}</p>
            </div>
            <div class="insights-section">
                <h4>💡 Actionable Insights</h4>
                <p>${result.insights}</p>
            </div>
        </div>
    `;
    
    document.getElementById('resultCard').innerHTML = resultHTML;
}
```

## Troubleshooting

### Common Issues

1. **Ollama not starting:**
   ```bash
   # Check if Ollama is running
   ps aux | grep ollama
   
   # Start Ollama manually
   ollama serve
   ```

2. **Model not found:**
   ```bash
   # List available models
   ollama list
   
   # Pull missing model
   ollama pull llama3.1:8b
   ```

3. **Connection refused:**
   - Verify Ollama is running on port 11434
   - Check firewall settings
   - Ensure correct host configuration

4. **Out of memory:**
   - Use smaller models (phi3:mini, gemma:2b)
   - Increase system RAM
   - Close other applications

### Performance Optimization

1. **GPU Acceleration:**
   ```bash
   # Install CUDA drivers for NVIDIA GPU acceleration
   # Ollama will automatically use GPU if available
   ```

2. **Model Management:**
   ```bash
   # Remove unused models to save space
   ollama rm unused_model_name
   
   # List model sizes
   ollama list
   ```

3. **Memory Settings:**
   ```bash
   # Set memory limits
   export OLLAMA_MAX_LOADED_MODELS=1
   export OLLAMA_MAX_VRAM=4GB
   ```

## Advanced Features

### 1. Model Router

Automatically select the best model based on query type:

```python
class ModelRouter:
    def __init__(self):
        self.models = {
            'explanation': 'llama3.1:8b',
            'insights': 'mistral:7b',
            'chat': 'phi3:mini',
            'analysis': 'llama3.1:70b'
        }
    
    def get_model_for_task(self, task: str) -> str:
        return self.models.get(task, 'llama3.1:8b')
```

### 2. Response Caching

Cache Ollama responses to reduce latency:

```python
import hashlib
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_ollama_query(prompt_hash: str, model: str) -> str:
    # Cache responses for identical prompts
    pass
```

### 3. Streaming Responses

For real-time response streaming:

```python
def stream_ollama_response(prompt: str):
    payload = {
        "model": self.model_name,
        "prompt": prompt,
        "stream": True
    }
    
    response = requests.post(f"{self.api_url}/generate", 
                           json=payload, stream=True)
    
    for line in response.iter_lines():
        if line:
            yield json.loads(line)['response']
```

## Integration with MCP

Ollama can be integrated with MCP for enhanced tool capabilities:

```python
# Add to MCP server
@app.tool("ollama_explain")
async def ollama_explain_tool(vehicle_data: dict, predicted_price: float):
    """Use Ollama to explain vehicle price prediction."""
    if OLLAMA_AVAILABLE:
        return ollama_agent.generate_explanation(
            vehicle_data, {}, predicted_price
        )
    return "Ollama not available for enhanced explanations"
```

This comprehensive Ollama integration provides local LLM capabilities while maintaining system reliability and performance.
