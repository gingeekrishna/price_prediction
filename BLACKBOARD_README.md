# Blackboard/Coordinator Pattern Integration

This document describes the Blackboard/Coordinator pattern implementation for enhanced agent coordination in the Vehicle Price Prediction system.

## Overview

The Blackboard pattern is an architectural design pattern where multiple specialized agents (knowledge sources) collaborate by reading from and writing to a shared blackboard (global data structure). A coordinator manages the workflow and ensures proper sequencing of agent activities.

## Architecture

### Core Components

1. **BlackboardCoordinator**: Central coordination hub
2. **BlackboardMessage**: Structured communication format
3. **BlackboardAgent**: Base class for coordinated agents
4. **VehiclePriceWorkflowCoordinator**: High-level workflow orchestrator

### Message Types

The system supports the following message types:

- `PREDICTION_REQUEST`: Initial price prediction requests
- `MARKET_DATA`: Market condition information
- `PREDICTION_RESULT`: Price prediction results
- `EXPLANATION`: Detailed prediction explanations
- `INSIGHT`: Actionable recommendations
- `ERROR`: Error conditions and diagnostics
- `STATUS_UPDATE`: Workflow status updates
- `COORDINATION_REQUEST`: Agent coordination requests

## Agent Architecture

### Specialized Blackboard Agents

#### 1. BlackboardMarketAgent
- **Purpose**: Provides market data with intelligent caching
- **Subscriptions**: `PREDICTION_REQUEST`, `MARKET_DATA`
- **Capabilities**:
  - 5-minute data caching
  - Fresh data on demand
  - Automatic market data provisioning

#### 2. BlackboardPredictionAgent
- **Purpose**: Core price prediction with market data integration
- **Subscriptions**: `PREDICTION_REQUEST`, `MARKET_DATA`
- **Capabilities**:
  - Waits for market data before prediction
  - Tracks pending predictions
  - Model version tracking

#### 3. BlackboardExplainerAgent
- **Purpose**: Automatic explanation generation
- **Subscriptions**: `PREDICTION_RESULT`, `EXPLANATION`
- **Capabilities**:
  - Automatic explanations for all predictions
  - On-demand explanation requests
  - Ollama integration for enhanced explanations

#### 4. BlackboardInsightAgent
- **Purpose**: Actionable insights and recommendations
- **Subscriptions**: `EXPLANATION`, `INSIGHT`
- **Capabilities**:
  - Insight generation from explanations
  - Direct insight requests
  - Ollama-powered analysis

#### 5. BlackboardLoggerAgent
- **Purpose**: Comprehensive activity logging
- **Subscriptions**: All message types
- **Capabilities**:
  - Complete blackboard activity logging
  - Integration with existing database
  - Activity summarization

## API Endpoints

### Enhanced Prediction Endpoints

#### `/predict_coordinated`
Enhanced prediction using blackboard coordination:

```json
{
  "vehicle_age": 3,
  "mileage": 45000,
  "include_explanation": true,
  "include_insights": true
}
```

**Response:**
```json
{
  "request_id": "pred_1234567890",
  "predicted_price": 22500.0,
  "input_data": {...},
  "market_data": {...},
  "explanation": "Detailed explanation...",
  "recommendation": "Actionable insights...",
  "processing_time": 1.23,
  "workflow_complete": true,
  "coordination_enabled": true,
  "agents_used": ["market", "prediction", "explainer", "insight", "logger"],
  "workflow_pattern": "blackboard"
}
```

### Monitoring and Control Endpoints

#### `/blackboard/status`
Get current blackboard system status:

```json
{
  "blackboard_available": true,
  "status": {
    "coordinator_active": true,
    "active_requests": 2,
    "agents_status": {
      "market_agent": true,
      "prediction_agent": true,
      "explainer_agent": true,
      "insight_agent": true,
      "logger_agent": true
    },
    "blackboard_messages": 15,
    "use_ollama": true
  },
  "pattern": "blackboard_coordination"
}
```

#### `/blackboard/messages`
Retrieve blackboard messages for monitoring:

```
GET /blackboard/messages?message_type=PREDICTION_RESULT&limit=10
```

**Response:**
```json
{
  "messages": [
    {
      "id": "msg_123_1234567890",
      "message_type": "PREDICTION_RESULT",
      "sender": "prediction_agent",
      "timestamp": "2025-07-31T10:30:00Z",
      "priority": "HIGH",
      "data": {...},
      "processed_by": ["explainer_agent", "logger_agent"]
    }
  ],
  "count": 10,
  "total_messages": 45,
  "active_agents": ["market_agent", "prediction_agent", ...]
}
```

#### `/blackboard/workflow`
Create custom workflows:

```json
{
  "workflow_id": "custom_analysis",
  "steps": [
    {
      "name": "market_analysis",
      "agent": "market_agent",
      "action": "deep_analysis",
      "data": {"region": "US", "timeframe": "1_month"}
    },
    {
      "name": "prediction_batch",
      "agent": "prediction_agent", 
      "action": "batch_predict",
      "dependencies": ["market_analysis"],
      "data": {"vehicles": [...]}
    }
  ]
}
```

## Usage Examples

### Basic Coordinated Prediction

```python
from src.blackboard_agents import VehiclePriceWorkflowCoordinator

async def predict_with_coordination():
    # Create workflow coordinator
    workflow = VehiclePriceWorkflowCoordinator(use_ollama=True)
    workflow.start()
    
    try:
        # Make coordinated prediction
        result = await workflow.predict_price(
            vehicle_age=3,
            mileage=45000,
            include_explanation=True,
            include_insights=True,
            timeout=30.0
        )
        
        print(f"Predicted Price: ${result['predicted_price']:.2f}")
        print(f"Explanation: {result['explanation']}")
        print(f"Recommendation: {result['recommendation']}")
        
    finally:
        workflow.stop()
```

### Custom Agent Integration

```python
from src.coordinator import BlackboardAgent, MessageType, Priority

class CustomAnalysisAgent(BlackboardAgent):
    def __init__(self, coordinator):
        super().__init__("custom_analysis", coordinator)
        self.subscribe_to(MessageType.PREDICTION_RESULT)
    
    def handle_message(self, message):
        if message.message_type == MessageType.PREDICTION_RESULT:
            # Perform custom analysis
            analysis = self.perform_analysis(message.data)
            
            # Post results
            self.post_message(
                MessageType.INSIGHT,
                {"custom_analysis": analysis},
                Priority.MEDIUM
            )
```

### Workflow Monitoring

```python
# Monitor active workflows
status = workflow.get_workflow_status()
print(f"Active requests: {status['active_requests']}")
print(f"Agent status: {status['agents_status']}")

# Get recent messages
messages = workflow.coordinator.get_messages(
    message_type=MessageType.PREDICTION_RESULT,
    limit=5
)

for msg in messages:
    print(f"Prediction from {msg.sender}: ${msg.data['predicted_price']}")
```

## Benefits

### 1. Loose Coupling
- Agents communicate through messages, not direct calls
- Easy to add/remove agents without affecting others
- Better fault isolation

### 2. Asynchronous Processing
- Agents work independently and asynchronously
- Better resource utilization
- Improved scalability

### 3. Workflow Coordination
- Complex multi-step processes managed centrally
- Dependency tracking and orchestration
- Error handling and recovery

### 4. Enhanced Monitoring
- Complete visibility into agent interactions
- Message history and debugging capabilities
- Performance tracking and optimization

### 5. Flexibility
- Dynamic workflow creation
- Runtime agent configuration
- Extensible architecture

## Configuration

### Environment Variables

```bash
# Blackboard configuration
BLACKBOARD_MAX_MESSAGES=1000
BLACKBOARD_CLEANUP_INTERVAL=300
BLACKBOARD_LOG_LEVEL=INFO

# Agent configuration
ENABLE_OLLAMA_AGENTS=true
MARKET_DATA_CACHE_DURATION=300
PREDICTION_TIMEOUT=30
```

### Advanced Configuration

```python
# Custom coordinator configuration
coordinator = BlackboardCoordinator(
    max_messages=2000,
    cleanup_interval=600
)

# Custom workflow with specific agents
workflow = VehiclePriceWorkflowCoordinator(use_ollama=True)
workflow.market_agent.cache_duration = 600  # 10 minutes cache
```

## Performance Considerations

### Message Volume Management
- Automatic cleanup of expired messages
- Configurable message limits
- Efficient message filtering and querying

### Agent Coordination
- Non-blocking message handling
- Parallel agent processing
- Timeout management for workflows

### Resource Usage
- Thread-safe operations
- Efficient memory usage
- Background cleanup processes

## Error Handling

### Message-Level Errors
```python
# Agents can post error messages
agent.post_message(
    MessageType.ERROR,
    {
        "error": "Prediction failed",
        "details": str(exception),
        "request_id": request_id
    },
    Priority.HIGH
)
```

### Workflow-Level Recovery
- Timeout handling for incomplete workflows
- Error message propagation
- Graceful degradation to standard agents

### Agent Failure Recovery
- Individual agent restart capability
- Message reprocessing on recovery
- Fault isolation between agents

## Testing

### Unit Tests
```python
def test_blackboard_coordination():
    coordinator = BlackboardCoordinator()
    coordinator.start()
    
    # Test message posting and retrieval
    msg_id = coordinator.post_message(
        MessageType.PREDICTION_REQUEST,
        {"vehicle_age": 3, "mileage": 45000},
        "test_client"
    )
    
    messages = coordinator.get_messages(MessageType.PREDICTION_REQUEST)
    assert len(messages) == 1
    assert messages[0].id == msg_id
    
    coordinator.stop()
```

### Integration Tests
```python
async def test_workflow_integration():
    workflow = VehiclePriceWorkflowCoordinator()
    workflow.start()
    
    result = await workflow.predict_price(3, 45000)
    
    assert result["predicted_price"] > 0
    assert "explanation" in result
    assert "recommendation" in result
    
    workflow.stop()
```

## Troubleshooting

### Common Issues

1. **Agent Not Responding**
   - Check agent status: `workflow.get_workflow_status()`
   - Verify message subscriptions
   - Check for agent exceptions in logs

2. **Message Not Processed**
   - Verify message type matches agent subscriptions
   - Check message expiration settings
   - Review message priority settings

3. **Workflow Timeout**
   - Increase timeout values
   - Check agent processing times
   - Verify all required agents are active

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Monitor message flow
workflow.coordinator.subscribe(
    MessageType.PREDICTION_REQUEST,
    lambda msg: print(f"Request: {msg.data}")
)
```

## Future Enhancements

### Planned Features

1. **Dynamic Agent Loading**
   - Runtime agent registration/deregistration
   - Plugin-based agent architecture
   - Hot-swappable agent implementations

2. **Advanced Workflow Patterns**
   - Conditional workflow branches
   - Loop and retry mechanisms
   - Complex dependency management

3. **Distributed Coordination**
   - Multi-node blackboard support
   - Network-based agent communication
   - Distributed workflow execution

4. **Performance Optimization**
   - Message compression
   - Batch message processing
   - Intelligent routing algorithms

### Integration Roadmap

- **Phase 1**: Core blackboard implementation ✅
- **Phase 2**: Enhanced workflow patterns 🔄
- **Phase 3**: Distributed coordination 📋
- **Phase 4**: Performance optimization 📋

## Contributing

When contributing to the blackboard pattern implementation:

1. Follow the existing message type conventions
2. Implement proper error handling in agents
3. Add comprehensive tests for new agents
4. Update documentation for new message types
5. Consider backward compatibility with standard agents

For questions or contributions, refer to the main project documentation and contribution guidelines.
