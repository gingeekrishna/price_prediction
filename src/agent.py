"""
Vehicle Price Prediction Agent

This module contains the main agent class for vehicle price prediction.
The agent follows a perceive-decide-act pattern for price prediction.
Includes Model Context Protocol (MCP) integration for standardized tool interfaces.
"""

import logging
from typing import Dict, Any, List, Union, Optional
import pandas as pd
import numpy as np
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPCapabilities:
    """
    Model Context Protocol capabilities for the Vehicle Price Agent.
    
    Provides standardized tool interfaces and metadata for MCP integration.
    """
    
    @staticmethod
    def get_tool_definitions() -> List[Dict[str, Any]]:
        """Get MCP tool definitions for this agent."""
        return [
            {
                "name": "predict_vehicle_price",
                "description": "Predict vehicle price using AI model with market data integration",
                "inputSchema": {
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
                            "description": "Vehicle brand (optional)"
                        },
                        "model": {
                            "type": "string",
                            "description": "Vehicle model (optional)"
                        }
                    },
                    "required": ["vehicle_age", "mileage"]
                }
            },
            {
                "name": "explain_prediction",
                "description": "Get detailed explanation of price prediction factors",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "vehicle_data": {"type": "object"},
                        "market_data": {"type": "object"},
                        "predicted_price": {"type": "number"}
                    },
                    "required": ["vehicle_data", "market_data", "predicted_price"]
                }
            }
        ]
    
    @staticmethod
    def get_server_info() -> Dict[str, Any]:
        """Get MCP server information."""
        return {
            "name": "vehicle-price-agent",
            "version": "1.0.0",
            "description": "AI agent for vehicle price prediction with market analysis",
            "capabilities": {
                "tools": True,
                "textGeneration": False,
                "multimodal": False
            },
            "vendor": "VehiclePricePredictor",
            "homepage": "https://github.com/gingeekrishna/price_prediction"
        }


class VehiclePriceAgent:
    """
    A vehicle price prediction agent that uses machine learning models
    to predict vehicle prices based on vehicle and market data.
    
    This agent follows the perceive-decide-act paradigm:
    - Perceive: Process and combine vehicle and market data
    - Decide: Use ML model to make price prediction
    - Act: Format and return the prediction result
    
    Includes MCP (Model Context Protocol) integration for standardized tool interfaces.
    
    Attributes:
        model: The trained machine learning model for price prediction
        feature_names: List of feature names expected by the model
        mcp_enabled: Whether MCP capabilities are enabled
    """
    
    def __init__(self, model: Any, feature_names: List[str], mcp_enabled: bool = True) -> None:
        """
        Initialize the Vehicle Price Agent.
        
        Args:
            model: A trained machine learning model with predict() method
            feature_names: List of feature names that the model expects
            mcp_enabled: Enable MCP (Model Context Protocol) capabilities
            
        Raises:
            ValueError: If model or feature_names are None/empty
        """
        if model is None:
            raise ValueError("Model cannot be None")
        if not feature_names:
            raise ValueError("Feature names cannot be empty")
            
        self.model = model
        self.feature_names = feature_names
        self.mcp_enabled = mcp_enabled
        
        if mcp_enabled:
            self.mcp_capabilities = MCPCapabilities()
            logger.info("MCP capabilities enabled")
        
        logger.info(f"Agent initialized with {len(feature_names)} features")

    def perceive(self, vehicle_data: Dict[str, Any], market_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Process and combine vehicle and market data into model-ready format.
        
        This method merges vehicle-specific data with market conditions,
        filters for model-expected features, and handles missing values.
        
        Args:
            vehicle_data: Dictionary containing vehicle-specific features
            market_data: Dictionary containing market condition data
            
        Returns:
            pandas.DataFrame: Processed data ready for model prediction
            
        Raises:
            ValueError: If input data is invalid
        """
        try:
            if not isinstance(vehicle_data, dict) or not isinstance(market_data, dict):
                raise ValueError("Input data must be dictionaries")
                
            # Combine vehicle and market data
            combined = {**vehicle_data, **market_data}
            logger.debug(f"Combined data keys: {list(combined.keys())}")
            
            # Filter for model features and fill missing values with 0
            filtered = {key: combined.get(key, 0) for key in self.feature_names}
            
            # Create DataFrame for model input
            df = pd.DataFrame([filtered])
            logger.info(f"Processed data shape: {df.shape}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error in perceive method: {str(e)}")
            raise

    def decide(self, processed_input: pd.DataFrame) -> float:
        """
        Use the ML model to predict vehicle price.
        
        Args:
            processed_input: DataFrame containing processed features
            
        Returns:
            float: Predicted vehicle price
            
        Raises:
            ValueError: If prediction fails or input is invalid
        """
        try:
            logger.debug("Processed input:")
            logger.debug(f"Shape: {processed_input.shape}")
            logger.debug(f"Columns: {processed_input.columns.tolist()}")
            
            # Log model feature expectations if available
            try:
                expected_features = list(self.model.feature_names_in_)
                logger.debug(f"Model expects features: {expected_features}")
            except AttributeError:
                logger.warning("Model feature names not available")

            # Make prediction
            prediction = self.model.predict(processed_input)[0]
            
            # Validate prediction
            if not isinstance(prediction, (int, float, np.number)):
                raise ValueError(f"Invalid prediction type: {type(prediction)}")
            if prediction < 0:
                logger.warning(f"Negative prediction detected: {prediction}")
                
            logger.info(f"Prediction made: ${prediction:,.2f}")
            return float(prediction)
            
        except Exception as e:
            logger.error(f"Error in decide method: {str(e)}")
            raise

    def act(self, prediction: float) -> str:
        """
        Format the prediction into a user-friendly response.
        
        Args:
            prediction: The predicted price value
            
        Returns:
            str: Formatted price recommendation string
            
        Raises:
            ValueError: If prediction is invalid
        """
        try:
            if not isinstance(prediction, (int, float)):
                raise ValueError(f"Prediction must be numeric, got {type(prediction)}")
                
            formatted_price = f"${prediction:,.2f}"
            response = f"Recommended price: {formatted_price}"
            logger.info(f"Action response: {response}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error in act method: {str(e)}")
            raise

    def run(self, vehicle_data: Dict[str, Any], market_data: Dict[str, Any]) -> str:
        """
        Execute the complete perception-decision-action cycle.
        
        This is the main method that orchestrates the entire prediction process:
        1. Perceive: Process input data
        2. Decide: Make price prediction
        3. Act: Format and return result
        
        Args:
            vehicle_data: Dictionary containing vehicle-specific features
            market_data: Dictionary containing market condition data
            
        Returns:
            str: Formatted price recommendation
            
        Raises:
            Exception: If any step in the process fails
        """
        try:
            logger.info("Starting price prediction cycle")
            
            # Perceive: Process input data
            processed = self.perceive(vehicle_data, market_data)
            
            # Decide: Make prediction
            decision = self.decide(processed)
            
            # Act: Format response
            action = self.act(decision)
            
            logger.info("Price prediction cycle completed successfully")
            return action
            
        except Exception as e:
            logger.error(f"Error in run method: {str(e)}")
            raise

    # MCP Integration Methods
    
    def get_mcp_tools(self) -> List[Dict[str, Any]]:
        """
        Get MCP tool definitions for this agent.
        
        Returns:
            List[Dict]: MCP tool definitions
        """
        if not self.mcp_enabled:
            return []
        
        return self.mcp_capabilities.get_tool_definitions()
    
    def get_mcp_server_info(self) -> Dict[str, Any]:
        """
        Get MCP server information.
        
        Returns:
            Dict: MCP server metadata
        """
        if not self.mcp_enabled:
            return {}
        
        return self.mcp_capabilities.get_server_info()
    
    async def handle_mcp_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP tool calls for this agent.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            
        Returns:
            Dict: Tool execution result
            
        Raises:
            ValueError: If tool is not supported
        """
        if not self.mcp_enabled:
            raise ValueError("MCP capabilities not enabled")
        
        if tool_name == "predict_vehicle_price":
            return await self._mcp_predict_price(arguments)
        elif tool_name == "explain_prediction":
            return await self._mcp_explain_prediction(arguments)
        else:
            raise ValueError(f"Unsupported MCP tool: {tool_name}")
    
    async def _mcp_predict_price(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        MCP tool implementation for price prediction.
        
        Args:
            args: Tool arguments containing vehicle data
            
        Returns:
            Dict: Prediction result with metadata
        """
        try:
            vehicle_age = args.get("vehicle_age")
            mileage = args.get("mileage")
            brand = args.get("brand", "Unknown")
            model_name = args.get("model", "Unknown")
            
            # Create vehicle data dict
            vehicle_data = {
                "age": vehicle_age,
                "mileage": mileage,
                "brand": brand,
                "model": model_name
            }
            
            # Mock market data (in real implementation, this would come from market agent)
            market_data = {
                "market_index": 1100.0,
                "fuel_price": 3.75
            }
            
            # Run prediction
            result = self.run(vehicle_data, market_data)
            
            # Extract price from result string
            price_str = result.replace("Recommended price: $", "").replace(",", "")
            predicted_price = float(price_str)
            
            return {
                "tool": "predict_vehicle_price",
                "result": {
                    "predicted_price": predicted_price,
                    "currency": "USD",
                    "vehicle_info": {
                        "age_years": vehicle_age,
                        "mileage_km": mileage,
                        "brand": brand,
                        "model": model_name
                    },
                    "market_conditions": market_data,
                    "formatted_result": result,
                    "timestamp": datetime.now().isoformat(),
                    "confidence": "High" if 10000 <= predicted_price <= 100000 else "Medium"
                },
                "success": True
            }
            
        except Exception as e:
            logger.error(f"MCP predict_price error: {str(e)}")
            return {
                "tool": "predict_vehicle_price",
                "error": str(e),
                "success": False
            }
    
    async def _mcp_explain_prediction(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        MCP tool implementation for prediction explanation.
        
        Args:
            args: Tool arguments containing prediction data
            
        Returns:
            Dict: Explanation result
        """
        try:
            vehicle_data = args.get("vehicle_data", {})
            market_data = args.get("market_data", {})
            predicted_price = args.get("predicted_price")
            
            # Generate explanation (simplified version)
            explanation = f"""
            Price Prediction Explanation:
            
            Vehicle Factors:
            - Age: {vehicle_data.get('age', 'N/A')} years (older vehicles typically have lower values)
            - Mileage: {vehicle_data.get('mileage', 'N/A')} km (higher mileage typically reduces value)
            - Brand: {vehicle_data.get('brand', 'N/A')} (brand reputation affects resale value)
            
            Market Factors:
            - Market Index: {market_data.get('market_index', 'N/A')} (overall market health)
            - Fuel Price: ${market_data.get('fuel_price', 'N/A')} (affects vehicle operational costs)
            
            Predicted Price: ${predicted_price:,.2f}
            
            This prediction is based on machine learning analysis of historical vehicle sales data
            combined with current market conditions.
            """
            
            return {
                "tool": "explain_prediction",
                "result": {
                    "explanation": explanation.strip(),
                    "factors": {
                        "vehicle_age": {
                            "value": vehicle_data.get('age'),
                            "impact": "Negative correlation with price"
                        },
                        "mileage": {
                            "value": vehicle_data.get('mileage'),
                            "impact": "Negative correlation with price"
                        },
                        "market_conditions": {
                            "market_index": market_data.get('market_index'),
                            "fuel_price": market_data.get('fuel_price'),
                            "impact": "Varies based on economic conditions"
                        }
                    },
                    "predicted_price": predicted_price,
                    "timestamp": datetime.now().isoformat()
                },
                "success": True
            }
            
        except Exception as e:
            logger.error(f"MCP explain_prediction error: {str(e)}")
            return {
                "tool": "explain_prediction",
                "error": str(e),
                "success": False
            }
