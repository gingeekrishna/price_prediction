"""
Vehicle Price Prediction Agent

This module contains the main agent class for vehicle price prediction.
The agent follows a perceive-decide-act pattern for price prediction.
"""

import logging
from typing import Dict, Any, List, Union
import pandas as pd
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VehiclePriceAgent:
    """
    A vehicle price prediction agent that uses machine learning models
    to predict vehicle prices based on vehicle and market data.
    
    This agent follows the perceive-decide-act paradigm:
    - Perceive: Process and combine vehicle and market data
    - Decide: Use ML model to make price prediction
    - Act: Format and return the prediction result
    
    Attributes:
        model: The trained machine learning model for price prediction
        feature_names: List of feature names expected by the model
    """
    
    def __init__(self, model: Any, feature_names: List[str]) -> None:
        """
        Initialize the Vehicle Price Agent.
        
        Args:
            model: A trained machine learning model with predict() method
            feature_names: List of feature names that the model expects
            
        Raises:
            ValueError: If model or feature_names are None/empty
        """
        if model is None:
            raise ValueError("Model cannot be None")
        if not feature_names:
            raise ValueError("Feature names cannot be empty")
            
        self.model = model
        self.feature_names = feature_names
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
