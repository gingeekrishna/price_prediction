"""
Model Context Protocol (MCP) Server for Vehicle Price Prediction

This module implements an MCP server that exposes the vehicle price prediction
agent functionality through standardized MCP tools and interfaces.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

try:
    from mcp import McpServer, Tool, TextContent
    from mcp.types import CallToolRequest, CallToolResult
except ImportError:
    print("Warning: MCP package not installed. Install with: pip install model-context-protocol")
    # Fallback implementations for development
    class McpServer:
        def __init__(self, name: str, version: str): pass
        def list_tools(self): return []
        def call_tool(self, request): pass
    
    class Tool:
        def __init__(self, name: str, description: str, input_schema: dict): pass
    
    class TextContent:
        def __init__(self, text: str): pass

from src.agents.model_agent import PriceModelAgent
from src.agents.market_data_agent import MarketDataAgent
from src.agents.explainer_agent import ExplainerAgentRAG
from src.agents.insight_agent import InsightAgent
from src.agents.logger_agent import LoggerAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VehiclePriceMCPServer:
    """
    MCP Server for Vehicle Price Prediction
    
    Provides standardized MCP tools for:
    - Vehicle price prediction
    - Market data retrieval
    - Prediction explanations
    - Insights and recommendations
    """
    
    def __init__(self):
        """Initialize the MCP server with agent instances."""
        self.server = McpServer("vehicle-price-prediction", "1.0.0")
        
        # Initialize agents
        self.model_agent = PriceModelAgent()
        self.market_agent = MarketDataAgent()
        self.explainer_agent = ExplainerAgentRAG()
        self.insight_agent = InsightAgent()
        self.logger_agent = LoggerAgent()
        
        # Register tools
        self._register_tools()
        
        logger.info("Vehicle Price MCP Server initialized")
    
    def _register_tools(self):
        """Register MCP tools with the server."""
        
        # Tool 1: Predict Vehicle Price
        predict_tool = Tool(
            name="predict_vehicle_price",
            description="Predict vehicle price based on age, mileage, and market conditions",
            input_schema={
                "type": "object",
                "properties": {
                    "vehicle_age": {
                        "type": "number",
                        "description": "Age of the vehicle in years",
                        "minimum": 0,
                        "maximum": 50
                    },
                    "mileage": {
                        "type": "number",
                        "description": "Vehicle mileage in kilometers",
                        "minimum": 0
                    },
                    "brand": {
                        "type": "string",
                        "description": "Vehicle brand (optional)",
                        "enum": ["Toyota", "Honda", "Ford", "BMW", "Mercedes", "Audi", "Other"]
                    },
                    "model": {
                        "type": "string",
                        "description": "Vehicle model (optional)"
                    }
                },
                "required": ["vehicle_age", "mileage"]
            }
        )
        
        # Tool 2: Get Market Data
        market_tool = Tool(
            name="get_market_data",
            description="Retrieve current market data and trends",
            input_schema={
                "type": "object",
                "properties": {
                    "region": {
                        "type": "string",
                        "description": "Market region",
                        "default": "global"
                    }
                }
            }
        )
        
        # Tool 3: Explain Prediction
        explain_tool = Tool(
            name="explain_prediction",
            description="Get detailed explanation of price prediction factors",
            input_schema={
                "type": "object",
                "properties": {
                    "vehicle_age": {
                        "type": "number",
                        "description": "Age of the vehicle in years"
                    },
                    "mileage": {
                        "type": "number",
                        "description": "Vehicle mileage in kilometers"
                    },
                    "predicted_price": {
                        "type": "number",
                        "description": "The predicted price to explain"
                    }
                },
                "required": ["vehicle_age", "mileage", "predicted_price"]
            }
        )
        
        # Tool 4: Get Insights and Recommendations
        insight_tool = Tool(
            name="get_insights",
            description="Get actionable insights and recommendations based on prediction",
            input_schema={
                "type": "object",
                "properties": {
                    "predicted_price": {
                        "type": "number",
                        "description": "The predicted price"
                    },
                    "explanation": {
                        "type": "string",
                        "description": "Explanation of the prediction"
                    }
                },
                "required": ["predicted_price"]
            }
        )
        
        # Register tools with server
        self.server.list_tools = lambda: [predict_tool, market_tool, explain_tool, insight_tool]
        self.server.call_tool = self._handle_tool_call
    
    async def _handle_tool_call(self, request: CallToolRequest) -> CallToolResult:
        """Handle MCP tool calls."""
        try:
            tool_name = request.params.name
            arguments = request.params.arguments or {}
            
            logger.info(f"Handling tool call: {tool_name} with args: {arguments}")
            
            if tool_name == "predict_vehicle_price":
                result = await self._predict_vehicle_price(arguments)
            elif tool_name == "get_market_data":
                result = await self._get_market_data(arguments)
            elif tool_name == "explain_prediction":
                result = await self._explain_prediction(arguments)
            elif tool_name == "get_insights":
                result = await self._get_insights(arguments)
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
            
            return CallToolResult(
                content=[TextContent(text=json.dumps(result, indent=2))],
                isError=False
            )
            
        except Exception as e:
            logger.error(f"Error handling tool call: {str(e)}")
            return CallToolResult(
                content=[TextContent(text=f"Error: {str(e)}")],
                isError=True
            )
    
    async def _predict_vehicle_price(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle vehicle price prediction."""
        vehicle_age = args.get("vehicle_age")
        mileage = args.get("mileage")
        brand = args.get("brand", "Unknown")
        model = args.get("model", "Unknown")
        
        # Get market data
        market_data = self.market_agent.fetch()
        
        # Prepare input for model
        full_input = {
            "vehicle_age": vehicle_age,
            "mileage": mileage,
            "market_index": market_data["market_index"],
            "fuel_price": market_data["fuel_price"]
        }
        
        # Make prediction
        predicted_price = self.model_agent.predict(full_input)
        
        # Get explanation and insights
        explanation = self.explainer_agent.explain(full_input, predicted_price)
        recommendation = self.insight_agent.recommend_action(predicted_price, explanation)
        
        # Log the prediction
        self.logger_agent.log(full_input, predicted_price)
        
        return {
            "predicted_price": predicted_price,
            "currency": "USD",
            "vehicle_info": {
                "age_years": vehicle_age,
                "mileage_km": mileage,
                "brand": brand,
                "model": model
            },
            "market_conditions": market_data,
            "explanation": explanation,
            "recommendation": recommendation,
            "timestamp": datetime.now().isoformat(),
            "confidence": "High" if 10000 <= predicted_price <= 100000 else "Medium"
        }
    
    async def _get_market_data(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle market data retrieval."""
        region = args.get("region", "global")
        
        market_data = self.market_agent.fetch()
        
        return {
            "region": region,
            "market_index": market_data["market_index"],
            "fuel_price": market_data["fuel_price"],
            "timestamp": datetime.now().isoformat(),
            "source": "MarketDataAgent",
            "currency": "USD"
        }
    
    async def _explain_prediction(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle prediction explanation."""
        vehicle_age = args.get("vehicle_age")
        mileage = args.get("mileage")
        predicted_price = args.get("predicted_price")
        
        # Get current market data
        market_data = self.market_agent.fetch()
        
        # Prepare input for explanation
        full_input = {
            "vehicle_age": vehicle_age,
            "mileage": mileage,
            "market_index": market_data["market_index"],
            "fuel_price": market_data["fuel_price"]
        }
        
        # Get detailed explanation
        explanation = self.explainer_agent.explain(full_input, predicted_price)
        
        return {
            "prediction_explanation": explanation,
            "factors": {
                "vehicle_age": {
                    "value": vehicle_age,
                    "impact": "Higher age typically decreases value"
                },
                "mileage": {
                    "value": mileage,
                    "impact": "Higher mileage typically decreases value"
                },
                "market_conditions": {
                    "market_index": market_data["market_index"],
                    "fuel_price": market_data["fuel_price"],
                    "impact": "Market conditions affect overall pricing"
                }
            },
            "predicted_price": predicted_price,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _get_insights(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle insights and recommendations."""
        predicted_price = args.get("predicted_price")
        explanation = args.get("explanation", "")
        
        recommendation = self.insight_agent.recommend_action(predicted_price, explanation)
        
        return {
            "predicted_price": predicted_price,
            "insights": recommendation,
            "action_items": [
                "Compare with similar vehicles in the market",
                "Consider timing of sale/purchase based on market trends",
                "Factor in additional costs (insurance, maintenance, etc.)"
            ],
            "confidence_level": "High" if 10000 <= predicted_price <= 100000 else "Medium",
            "timestamp": datetime.now().isoformat()
        }
    
    def run(self, host: str = "localhost", port: int = 3000):
        """Run the MCP server."""
        logger.info(f"Starting Vehicle Price MCP Server on {host}:{port}")
        
        # Note: This is a simplified runner. In a real MCP implementation,
        # you would use the proper MCP transport layer (stdio, websocket, etc.)
        try:
            print(f"🚗 Vehicle Price MCP Server")
            print(f"📍 Running on {host}:{port}")
            print(f"🔧 Available tools: predict_vehicle_price, get_market_data, explain_prediction, get_insights")
            print(f"📋 Use MCP client to connect and interact with tools")
            print(f"⏹️  Press Ctrl+C to stop")
            
            # Keep server running
            asyncio.get_event_loop().run_forever()
            
        except KeyboardInterrupt:
            logger.info("Shutting down MCP server...")
        except Exception as e:
            logger.error(f"Server error: {str(e)}")


def main():
    """Main entry point for MCP server."""
    server = VehiclePriceMCPServer()
    server.run()


if __name__ == "__main__":
    main()
