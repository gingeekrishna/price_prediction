# AWS Bedrock Integration Documentation 🔮

## Overview

The Vehicle Price Prediction System now includes **AWS Bedrock integration**, providing access to enterprise-grade foundation models for enhanced AI-powered vehicle price analysis.

## Supported Foundation Models

### Amazon Bedrock Models
- **Claude 3 Sonnet** (`anthropic.claude-3-sonnet-20240229-v1:0`) - Advanced reasoning and analysis
- **Claude 3 Haiku** (`anthropic.claude-3-haiku-20240307-v1:0`) - Fast, efficient responses
- **Amazon Titan Text Express** (`amazon.titan-text-express-v1`) - High-quality text generation
- **AI21 Jurassic-2 Ultra** (`ai21.j2-ultra-v1`) - Multilingual capabilities
- **Cohere Command** (`cohere.command-text-v14`) - Instruction-following AI

## API Endpoints

### `/predict_with_bedrock`
Enhanced prediction endpoint using AWS Bedrock foundation models.

**Request:**
```json
{
    "vehicle_age": 3,
    "mileage": 35000,
    "make": "Toyota",
    "model": "Camry",
    "year": 2021,
    "bedrock_model": "anthropic.claude-3-sonnet-20240229-v1:0"
}
```

**Response:**
```json
{
    "predicted_price": 22500.0,
    "explanation": "🔮 AWS Bedrock AI Analysis:\n\nYour 2021 Toyota Camry...",
    "recommendation": "🔮 Advanced AI analysis complete...",
    "market_data": {...},
    "llm_provider": "bedrock",
    "bedrock_model": "anthropic.claude-3-sonnet-20240229-v1:0",
    "timestamp": "2024-01-15T10:30:00"
}
```

### `/bedrock/status`
Check AWS Bedrock availability and supported models.

**Response:**
```json
{
    "available": true,
    "models": [
        "anthropic.claude-3-sonnet-20240229-v1:0",
        "amazon.titan-text-express-v1",
        "ai21.j2-ultra-v1",
        "cohere.command-text-v14"
    ],
    "status": "connected",
    "provider": "AWS Bedrock",
    "region": "us-east-1"
}
```

## Configuration

### AWS Credentials Setup

#### Option 1: AWS CLI Configuration
```bash
aws configure
# Enter your AWS Access Key ID, Secret Access Key, Region, and Output format
```

#### Option 2: Environment Variables
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

#### Option 3: IAM Role (for EC2/ECS)
Attach an IAM role with Bedrock permissions to your compute instance.

### Required AWS Permissions

Your AWS credentials need the following permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream",
                "bedrock:ListFoundationModels"
            ],
            "Resource": "*"
        }
    ]
}
```

### Model Access Setup

1. **Enable Model Access**: Go to AWS Bedrock console → Model access
2. **Request Access**: Enable access for desired foundation models
3. **Wait for Approval**: Some models require approval (usually immediate)

## Multi-LLM Fallback Chain

The system uses an intelligent fallback chain for maximum reliability:

```
🔮 AWS Bedrock (Primary) 
    ↓ (if unavailable)
🧠 Claude AI (Secondary)
    ↓ (if unavailable)  
🤖 Ollama Local AI (Tertiary)
    ↓ (if unavailable)
📊 Standard Analysis (Fallback)
```

## Testing Bedrock Integration

Use the provided test script:

```bash
python test_bedrock_integration.py
```

This will test:
- ✅ BedrockAgent initialization
- ✅ Foundation model availability  
- ✅ Explanation generation
- ✅ Integration with ExplainerAgentRAG
- ✅ Multi-model support

## Troubleshooting

### Common Issues

#### 1. "AWS Bedrock not available"
- **Cause**: Missing or invalid AWS credentials
- **Solution**: Configure AWS credentials using one of the methods above
- **Check**: Run `aws sts get-caller-identity` to verify credentials

#### 2. "Model not available in region"
- **Cause**: Foundation model not supported in your AWS region
- **Solution**: Switch to a supported region (us-east-1, us-west-2, eu-west-1)
- **Check**: Verify model availability in AWS Bedrock console

#### 3. "Access denied to model"
- **Cause**: Model access not enabled in Bedrock console
- **Solution**: Enable model access in AWS Bedrock console
- **Wait**: Some models require approval time

#### 4. "Rate limit exceeded"
- **Cause**: Too many requests to Bedrock models
- **Solution**: Implement request throttling or upgrade your limits
- **Check**: Monitor CloudWatch metrics for Bedrock usage

### Debugging Tips

1. **Enable Debug Logging**:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Check Bedrock Status**:
   ```bash
   curl http://localhost:8000/bedrock/status
   ```

3. **Test Individual Models**:
   ```python
   from src.agents.bedrock_agent import BedrockAgent
   agent = BedrockAgent(model_id="anthropic.claude-3-sonnet-20240229-v1:0")
   print(agent.available)
   ```

## Cost Optimization

### Model Selection Guide

| Model | Speed | Quality | Cost | Use Case |
|-------|-------|---------|------|----------|
| Claude 3 Haiku | ⚡⚡⚡ | ⭐⭐⭐ | 💰 | High-volume, fast responses |
| Claude 3 Sonnet | ⚡⚡ | ⭐⭐⭐⭐⭐ | 💰💰 | Balanced performance |
| Titan Text Express | ⚡⚡ | ⭐⭐⭐ | 💰 | Cost-effective generation |
| AI21 Jurassic-2 | ⚡ | ⭐⭐⭐⭐ | 💰💰💰 | Complex reasoning |
| Cohere Command | ⚡⚡ | ⭐⭐⭐⭐ | 💰💰 | Instruction following |

### Cost-Saving Tips

1. **Use Haiku for High Volume**: Switch to Claude 3 Haiku for frequent requests
2. **Implement Caching**: Cache similar requests to reduce API calls
3. **Request Throttling**: Limit concurrent requests to avoid rate limits
4. **Monitor Usage**: Set up CloudWatch alarms for cost tracking

## Security Best Practices

1. **Use IAM Roles**: Prefer IAM roles over access keys when possible
2. **Least Privilege**: Grant only required Bedrock permissions
3. **Rotate Credentials**: Regularly rotate AWS access keys
4. **Network Security**: Use VPC endpoints for private Bedrock access
5. **Audit Logs**: Enable CloudTrail for API call auditing

## Performance Optimization

### Response Time Optimization

1. **Regional Selection**: Choose the AWS region closest to your users
2. **Model Selection**: Use faster models (Haiku) for time-sensitive requests
3. **Connection Pooling**: Reuse HTTP connections to Bedrock
4. **Parallel Processing**: Process multiple requests concurrently

### Example Performance Comparison

| Provider | Average Response Time | Quality Score |
|----------|----------------------|---------------|
| AWS Bedrock Claude 3 | 2.1s | 9.5/10 |
| Direct Claude API | 1.8s | 9.5/10 |
| Ollama Local | 9.2s | 8.0/10 |
| Standard Analysis | 0.1s | 6.0/10 |

## Architecture Integration

### BedrockAgent Class Structure

```python
class BedrockAgent:
    """AWS Bedrock integration for vehicle price prediction."""
    
    def __init__(self, model_id=None, region="us-east-1")
    def generate_explanation(self, vehicle_data, market_data, predicted_price)
    def invoke_model(self, prompt, **kwargs)
    @property
    def available(self) -> bool
```

### BedrockAgentManager Class

```python
class BedrockAgentManager:
    """Manages multiple Bedrock agents with different models."""
    
    def get_agent(self, model_id: str) -> BedrockAgent
    def get_available_models(self) -> List[str]
    def get_best_agent_for_task(self, task_type: str) -> BedrockAgent
```

## Future Roadmap

### Planned Enhancements

1. **🔄 Model Auto-Selection**: Intelligent model selection based on request complexity
2. **📊 Performance Analytics**: Advanced metrics and performance tracking  
3. **🎯 Custom Fine-Tuning**: Support for custom-trained Bedrock models
4. **🔗 Multi-Modal Support**: Integration with vision and embedding models
5. **⚡ Streaming Responses**: Real-time streaming for long-form explanations

### Integration Possibilities

- **Amazon Kendra**: Enhanced document retrieval
- **Amazon Comprehend**: Advanced sentiment analysis
- **Amazon Translate**: Multi-language support
- **Amazon Polly**: Text-to-speech capabilities

---

## Quick Start Example

```python
# Initialize Bedrock-enabled explainer
from src.agents.explainer_agent import ExplainerAgentRAG

explainer = ExplainerAgentRAG(
    use_bedrock=True,
    use_claude=True,
    use_ollama=True,
    llm_provider="auto"  # Smart selection
)

# Generate explanation
vehicle_data = {
    'vehicle_age': 5,
    'mileage': 50000,
    'make': 'Toyota', 
    'model': 'Camry',
    'year': 2019
}

market_data = {
    'market_index': 1050,
    'fuel_price': 3.25
}

explanation = explainer.explain(vehicle_data, 18500.0)
print(explanation)  # Will use best available AI provider
```

Ready to leverage enterprise-grade AI for vehicle price predictions! 🚀
