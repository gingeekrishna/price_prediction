# Vehicle Price Prediction - MCP Integration

This document describes the Model Context Protocol (MCP) integration for the Vehicle Price Prediction agent.

## Overview

The Vehicle Price Prediction system now includes MCP (Model Context Protocol) support, enabling standardized tool interfaces for AI assistants and language models to interact with the price prediction functionality.

## MCP Configuration

### Server Configuration

The MCP server configuration is defined in `mcp_config.json`:

```json
{
  "mcpServers": {
    "vehicle-price-agent": {
      "command": "python",
      "args": ["-m", "src.mcp_server"],
      "env": {
        "PYTHONPATH": ".",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### Available Tools

The MCP server exposes the following tools:

#### 1. `predict_vehicle_price`
- **Description**: Predict vehicle price based on age, mileage, and market conditions
- **Required Parameters**:
  - `vehicle_age` (number): Age of the vehicle in years (0-50)
  - `mileage` (number): Vehicle mileage in kilometers (≥0)
- **Optional Parameters**:
  - `brand` (string): Vehicle brand
  - `model` (string): Vehicle model

#### 2. `get_market_data`
- **Description**: Retrieve current market data and trends
- **Parameters**:
  - `region` (string, optional): Market region (default: "global")

#### 3. `explain_prediction`
- **Description**: Get detailed explanation of price prediction factors
- **Required Parameters**:
  - `vehicle_age` (number): Age of the vehicle
  - `mileage` (number): Vehicle mileage
  - `predicted_price` (number): The predicted price to explain

#### 4. `get_insights`
- **Description**: Get actionable insights and recommendations
- **Required Parameters**:
  - `predicted_price` (number): The predicted price
- **Optional Parameters**:
  - `explanation` (string): Explanation of the prediction

## Running the MCP Server

### Option 1: Using the startup script
```bash
python run_mcp_server.py
```

### Option 2: Direct module execution
```bash
python -m src.mcp_server
```

### Option 3: Using the agent with MCP enabled
```python
from src.agent import VehiclePriceAgent
from src.model import load_model

# Load your trained model
model = load_model("src/model.pkl")
feature_names = ["vehicle_age", "mileage", "market_index", "fuel_price"]

# Initialize agent with MCP capabilities
agent = VehiclePriceAgent(model, feature_names, mcp_enabled=True)

# Get MCP tool definitions
tools = agent.get_mcp_tools()
print("Available MCP tools:", tools)

# Handle MCP tool calls
result = await agent.handle_mcp_tool_call(
    "predict_vehicle_price",
    {"vehicle_age": 3, "mileage": 45000}
)
print("Prediction result:", result)
```

## MCP Client Example

A demonstration client is provided in `mcp_client_example.py`:

```bash
python mcp_client_example.py
```

This will demonstrate:
- Listing available tools
- Making price predictions
- Retrieving market data
- Getting prediction explanations
- Obtaining insights and recommendations

## Integration with AI Assistants

### Claude Desktop Integration

To integrate with Claude Desktop, add the following to your Claude configuration:

```json
{
  "mcpServers": {
    "vehicle-price-predictor": {
      "command": "python",
      "args": ["run_mcp_server.py"],
      "cwd": "/path/to/vehicle-price-agent-multi"
    }
  }
}
```

### VS Code Integration

For VS Code with MCP support:

1. Install MCP extension
2. Add server configuration to workspace settings
3. Use MCP tools through the command palette

## Tool Response Format

All MCP tools return structured JSON responses:

```json
{
  "success": true,
  "result": {
    "predicted_price": 22500.0,
    "currency": "USD",
    "vehicle_info": {
      "age_years": 3,
      "mileage_km": 45000,
      "brand": "Toyota",
      "model": "Camry"
    },
    "market_conditions": {
      "market_index": 1125.0,
      "fuel_price": 3.80
    },
    "explanation": "Price prediction based on vehicle depreciation...",
    "recommendation": "Fair market value - good buying opportunity",
    "timestamp": "2025-07-31T10:30:00Z",
    "confidence": "High"
  }
}
```

## Error Handling

MCP tools include comprehensive error handling:

```json
{
  "success": false,
  "error": "Invalid vehicle age: must be between 0 and 50 years",
  "tool": "predict_vehicle_price"
}
```

## Logging

MCP server operations are logged to:
- Console output (INFO level)
- `mcp_server.log` file (detailed logging)

## Dependencies

MCP functionality requires additional dependencies:

```bash
# Note: MCP packages are in development
# Install from source when available
pip install model-context-protocol
```

## Development

### Adding New MCP Tools

1. Add tool definition to `MCPCapabilities.get_tool_definitions()`
2. Implement handler method in `VehiclePriceAgent`
3. Add route in `VehiclePriceMCPServer`
4. Update documentation

### Testing MCP Integration

Run the test suite with MCP-specific tests:

```bash
python -m pytest tests/ -k "mcp"
```

## Troubleshooting

### Common Issues

1. **Port conflicts**: Change server port in configuration
2. **Module import errors**: Ensure PYTHONPATH is set correctly
3. **Model loading issues**: Verify model file exists and is accessible

### Debug Mode

Enable debug logging:

```bash
LOG_LEVEL=DEBUG python run_mcp_server.py
```

## Security Considerations

- MCP server runs on localhost by default
- No authentication implemented (suitable for local development)
- For production use, implement proper authentication and HTTPS

## Future Enhancements

- WebSocket transport support
- Authentication and authorization
- Rate limiting
- Caching for improved performance
- Multi-model support
- Real-time market data integration
- **Blackboard coordination integration** - Enhanced agent coordination using blackboard pattern
- **Workflow orchestration** - Complex multi-agent workflows with dependency management
- **Agentic RAG integration** - Intelligent knowledge retrieval and generation capabilities

## Advanced Pattern Integration

The MCP integration works seamlessly with both the Blackboard/Coordinator pattern and the new Agentic RAG system for comprehensive AI capabilities:

### Combined Architecture

```python
from src.blackboard_agents import VehiclePriceWorkflowCoordinator
from src.agent import VehiclePriceAgent
from src.agentic_rag import AgenticRagCoordinator, KnowledgeStore

# Use all three patterns together
async def comprehensive_prediction():
    # Blackboard coordination with RAG
    workflow = VehiclePriceWorkflowCoordinator(
        use_ollama=True, 
        enable_rag=True
    )
    workflow.start()
    
    # MCP tools for standardized interfaces
    mcp_agent = VehiclePriceAgent(model, feature_names, mcp_enabled=True)
    
    try:
        # Enhanced prediction with all capabilities
        result = await workflow.predict_price(
            vehicle_age=3, 
            mileage=45000,
            include_rag_analysis=True
        )
        
        # Also available as MCP tool
        mcp_result = await mcp_agent.handle_mcp_tool_call(
            "predict_vehicle_price",
            {"vehicle_age": 3, "mileage": 45000}
        )
        
        # Direct RAG knowledge query
        rag_insight = await workflow.query_knowledge(
            "What factors influence this vehicle's depreciation?",
            {"predicted_price": result["predicted_price"]}
        )
        
        return {
            "coordinated_prediction": result,
            "mcp_prediction": mcp_result,
            "rag_insights": rag_insight,
            "integration_complete": True
        }
        
    finally:
        workflow.stop()
```

### API Endpoints

The system now provides five distinct prediction modes:

1. **Standard**: `/predict` - Basic agent coordination
2. **MCP**: MCP tools - Standardized tool interface
3. **Ollama**: `/predict_with_ollama` - Local LLM enhancement
4. **Coordinated**: `/predict_coordinated` - Full blackboard coordination
5. **RAG-Enhanced**: `/predict_rag_enhanced` - Knowledge-augmented predictions

### Architecture Patterns Available

| Pattern | Use Case | Benefits | Integration |
|---------|----------|----------|-------------|
| **Standard Agents** | Simple predictions | Fast, lightweight | Base layer |
| **MCP Integration** | AI assistant integration | Standardized, interoperable | Protocol layer |
| **Blackboard Coordination** | Complex workflows | Scalable, fault-tolerant | Coordination layer |
| **Agentic RAG** | Knowledge-enhanced responses | Learning, contextual | Intelligence layer |
| **Combined (All Patterns)** | Enterprise AI scenarios | Comprehensive capabilities | Full stack |

### RAG-Enhanced MCP Tools

```python
# Enhanced MCP tools with RAG capabilities
class RagEnhancedMCPAgent(VehiclePriceAgent):
    def __init__(self, model, feature_names, rag_coordinator):
        super().__init__(model, feature_names, mcp_enabled=True)
        self.rag_coordinator = rag_coordinator
    
    async def handle_mcp_tool_call(self, tool_name, parameters):
        # Standard MCP processing
        result = await super().handle_mcp_tool_call(tool_name, parameters)
        
        # Enhance with RAG if successful
        if result.get('success') and tool_name == 'predict_vehicle_price':
            try:
                # Query knowledge base for additional insights
                rag_query = f"Provide insights for {parameters.get('vehicle_age')}y vehicle"
                rag_result = await self.rag_coordinator.process_query(rag_query)
                
                # Add RAG insights to MCP response
                result['result']['rag_insights'] = {
                    'analysis': rag_result.get('response', ''),
                    'confidence': rag_result.get('confidence', 0.0),
                    'knowledge_sources': rag_result.get('sources', [])
                }
                
            except Exception as e:
                # Graceful degradation
                result['result']['rag_insights'] = {
                    'error': f"RAG enhancement failed: {str(e)}"
                }
        
        return result
```

## Contributing

When contributing MCP-related features:

1. Follow MCP specification standards
2. Add comprehensive tests
3. Update documentation
4. Ensure backward compatibility
5. **Consider blackboard pattern integration** for enhanced coordination
6. **Test with both MCP and blackboard endpoints** to ensure compatibility
7. **Integrate with RAG capabilities** for knowledge-enhanced responses
8. **Maintain pattern separation** to allow independent usage of each pattern

For more information about Model Context Protocol, visit: [MCP Documentation](https://modelcontextprotocol.io)
