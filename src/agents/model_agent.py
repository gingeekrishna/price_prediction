"""
Price Model Agent

This module contains the PriceModelAgent class responsible for
loading and managing the machine learning model for price predictions.
It provides a clean interface for model inference.
"""

import logging
import os
from typing import Dict, Any, Union
import pickle
import pandas as pd
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PriceModelAgent:
    """
    Agent responsible for managing and executing price prediction models.
    
    This agent handles model loading, caching, and prediction execution
    with proper error handling and logging.
    
    Attributes:
        model: The loaded machine learning model
        model_path: Path to the model file
        is_loaded: Whether the model is successfully loaded
    """
    
    def __init__(self, model_path: str = "src/model.pkl"):
        """
        Initialize the Price Model Agent.
        
        Args:
            model_path: Path to the pickled model file
            
        Raises:
            FileNotFoundError: If model file doesn't exist
            Exception: If model loading fails
        """
        # Convert relative path to absolute path
        if not os.path.isabs(model_path):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            model_path = os.path.join(project_root, model_path)
            
        self.model_path = model_path
        self.model = None
        self.is_loaded = False
        
        # Load the model during initialization
        self._load_model()
    
    def _load_model(self) -> None:
        """
        Load the machine learning model from the specified path.
        
        Raises:
            FileNotFoundError: If model file doesn't exist
            Exception: If model loading fails
        """
        try:
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model file not found: {self.model_path}")
            
            logger.info(f"Loading model from: {self.model_path}")
            
            with open(self.model_path, "rb") as f:
                self.model = pickle.load(f)
            
            # Validate loaded model
            if not hasattr(self.model, 'predict'):
                raise ValueError("Loaded object does not have a predict method")
            
            self.is_loaded = True
            logger.info("Model loaded successfully")
            
            # Log model information if available
            try:
                if hasattr(self.model, 'n_estimators'):
                    logger.info(f"Model type: Random Forest with {self.model.n_estimators} estimators")
                if hasattr(self.model, 'feature_names_in_'):
                    logger.info(f"Model expects {len(self.model.feature_names_in_)} features")
            except AttributeError:
                pass
                
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            self.is_loaded = False
            raise
    
    def predict(self, input_data: Dict[str, Any]) -> float:
        """
        Make a price prediction using the loaded model.
        
        Args:
            input_data: Dictionary containing feature values for prediction
            
        Returns:
            Predicted price as a float
            
        Raises:
            RuntimeError: If model is not loaded
            ValueError: If input data is invalid
            Exception: If prediction fails
        """
        try:
            if not self.is_loaded:
                raise RuntimeError("Model is not loaded. Cannot make predictions.")
            
            if not isinstance(input_data, dict):
                raise ValueError("Input data must be a dictionary")
            
            if not input_data:
                raise ValueError("Input data cannot be empty")
            
            logger.debug(f"Making prediction with input: {input_data}")
            
            # Convert input to DataFrame
            df = pd.DataFrame([input_data])
            
            # Make prediction
            prediction = self.model.predict(df)[0]
            
            # Validate prediction
            if not isinstance(prediction, (int, float, np.number)):
                raise ValueError(f"Invalid prediction type: {type(prediction)}")
            
            prediction_float = float(prediction)
            
            if prediction_float < 0:
                logger.warning(f"Negative prediction detected: {prediction_float}")
            
            logger.info(f"Prediction made: ${prediction_float:,.2f}")
            
            return prediction_float
            
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            raise
    
    def predict_with_confidence(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a prediction with confidence intervals (if model supports it).
        
        Args:
            input_data: Dictionary containing feature values for prediction
            
        Returns:
            Dictionary containing prediction and confidence information
        """
        try:
            # Get basic prediction
            prediction = self.predict(input_data)
            
            result = {
                'prediction': prediction,
                'confidence_interval': None,
                'feature_importance': None
            }
            
            # Try to get confidence intervals for ensemble models
            if hasattr(self.model, 'estimators_'):
                df = pd.DataFrame([input_data])
                
                # Get predictions from all estimators
                estimator_predictions = []
                for estimator in self.model.estimators_:
                    pred = estimator.predict(df)[0]
                    estimator_predictions.append(pred)
                
                # Calculate confidence interval (using standard deviation)
                mean_pred = np.mean(estimator_predictions)
                std_pred = np.std(estimator_predictions)
                
                confidence_interval = [
                    max(0, mean_pred - 1.96 * std_pred),  # Lower bound
                    mean_pred + 1.96 * std_pred           # Upper bound
                ]
                
                result['confidence_interval'] = confidence_interval
                result['prediction_std'] = std_pred
                
                logger.info(f"Confidence interval: ${confidence_interval[0]:,.2f} - ${confidence_interval[1]:,.2f}")
            
            # Get feature importance if available
            if hasattr(self.model, 'feature_importances_'):
                feature_names = df.columns.tolist()
                importances = self.model.feature_importances_
                
                feature_importance = dict(zip(feature_names, importances))
                result['feature_importance'] = feature_importance
            
            return result
            
        except Exception as e:
            logger.error(f"Prediction with confidence failed: {str(e)}")
            # Fall back to basic prediction
            return {
                'prediction': self.predict(input_data),
                'confidence_interval': None,
                'feature_importance': None
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model.
        
        Returns:
            Dictionary containing model metadata
        """
        if not self.is_loaded:
            return {'status': 'not_loaded', 'error': 'Model not loaded'}
        
        info = {
            'status': 'loaded',
            'model_path': self.model_path,
            'model_type': type(self.model).__name__
        }
        
        # Add model-specific information
        try:
            if hasattr(self.model, 'n_estimators'):
                info['n_estimators'] = self.model.n_estimators
            
            if hasattr(self.model, 'feature_names_in_'):
                info['expected_features'] = list(self.model.feature_names_in_)
                info['n_features'] = len(self.model.feature_names_in_)
            
            if hasattr(self.model, 'n_outputs_'):
                info['n_outputs'] = self.model.n_outputs_
                
            # Get file size
            if os.path.exists(self.model_path):
                file_size = os.path.getsize(self.model_path)
                info['file_size_mb'] = round(file_size / (1024 * 1024), 2)
                
        except Exception as e:
            logger.warning(f"Could not retrieve all model information: {e}")
        
        return info
    
    def reload_model(self) -> bool:
        """
        Reload the model from disk.
        
        Returns:
            True if reload successful, False otherwise
        """
        try:
            logger.info("Reloading model...")
            self._load_model()
            return self.is_loaded
        except Exception as e:
            logger.error(f"Model reload failed: {e}")
            return False
    
    def is_model_available(self) -> bool:
        """
        Check if the model is loaded and available for predictions.
        
        Returns:
            True if model is available, False otherwise
        """
        return self.is_loaded and self.model is not None
