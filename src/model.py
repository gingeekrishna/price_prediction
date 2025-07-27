"""
Machine Learning Model Training Module

This module provides functionality for training and evaluating
vehicle price prediction models using various ML algorithms.
"""

import logging
from typing import Tuple, Optional, Dict, Any
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from math import sqrt
import joblib
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def train_model(
    df: pd.DataFrame, 
    target: str = "price",
    test_size: float = 0.2,
    random_state: int = 42,
    n_estimators: int = 100,
    save_model: bool = True,
    model_path: str = "src/model.pkl"
) -> Tuple[Any, Dict[str, float]]:
    """
    Train a Random Forest model for vehicle price prediction.
    
    This function preprocesses the data, trains a Random Forest model,
    evaluates its performance, and optionally saves the trained model.
    
    Args:
        df: DataFrame containing features and target variable
        target: Name of the target column (default: "price")
        test_size: Proportion of data to use for testing (default: 0.2)
        random_state: Random seed for reproducibility (default: 42)
        n_estimators: Number of trees in the forest (default: 100)
        save_model: Whether to save the trained model (default: True)
        model_path: Path to save the model file (default: "src/model.pkl")
        
    Returns:
        Tuple containing:
            - Trained model object
            - Dictionary with evaluation metrics (RMSE, MAE, R²)
            
    Raises:
        ValueError: If target column is missing or data is insufficient
        Exception: If model training fails
    """
    try:
        logger.info("Starting model training process")
        
        # Validate input data
        if df is None or df.empty:
            raise ValueError("DataFrame cannot be None or empty")
        
        if target not in df.columns:
            raise ValueError(f"Target column '{target}' not found in DataFrame")
            
        if len(df) < 3:
            raise ValueError("Insufficient data for training (minimum 3 samples required)")
        
        # Prepare features and target
        logger.info(f"Dataset shape: {df.shape}")
        logger.info(f"Target column: {target}")
        
        # Drop date column if it exists and target column
        columns_to_drop = [target]
        if "date" in df.columns:
            columns_to_drop.append("date")
            
        X = df.drop(columns=columns_to_drop)
        y = df[target]
        
        logger.info(f"Features shape: {X.shape}")
        logger.info(f"Feature columns: {X.columns.tolist()}")
        
        # Check for missing values
        if X.isnull().sum().sum() > 0:
            logger.warning("Missing values detected in features")
            X = X.fillna(0)  # Simple imputation
            
        if y.isnull().sum() > 0:
            logger.warning("Missing values detected in target")
            # Remove rows with missing target values
            valid_indices = ~y.isnull()
            X = X[valid_indices]
            y = y[valid_indices]
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        logger.info(f"Training set size: {X_train.shape[0]}")
        logger.info(f"Test set size: {X_test.shape[0]}")
        
        # Initialize and train the model
        model = RandomForestRegressor(
            n_estimators=n_estimators, 
            random_state=random_state,
            n_jobs=-1  # Use all available cores
        )
        
        logger.info("Training Random Forest model...")
        model.fit(X_train, y_train)
        
        # Make predictions
        train_preds = model.predict(X_train)
        test_preds = model.predict(X_test)
        
        # Calculate evaluation metrics
        metrics = _calculate_metrics(y_train, train_preds, y_test, test_preds)
        
        # Log results
        logger.info("Model training completed successfully")
        logger.info(f"Training RMSE: {metrics['train_rmse']:.2f}")
        logger.info(f"Test RMSE: {metrics['test_rmse']:.2f}")
        logger.info(f"Test R²: {metrics['test_r2']:.4f}")
        logger.info(f"Test MAE: {metrics['test_mae']:.2f}")
        
        # Feature importance analysis
        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        logger.info("Top 5 most important features:")
        for idx, row in feature_importance.head().iterrows():
            logger.info(f"  {row['feature']}: {row['importance']:.4f}")
        
        # Save the model if requested
        if save_model:
            _save_model(model, model_path)
            
        return model, metrics
        
    except Exception as e:
        logger.error(f"Error in train_model: {str(e)}")
        raise


def _calculate_metrics(
    y_train: pd.Series, 
    train_preds: np.ndarray, 
    y_test: pd.Series, 
    test_preds: np.ndarray
) -> Dict[str, float]:
    """
    Calculate comprehensive evaluation metrics for the model.
    
    Args:
        y_train: Training target values
        train_preds: Training predictions
        y_test: Test target values
        test_preds: Test predictions
        
    Returns:
        Dictionary containing various evaluation metrics
    """
    try:
        # Training metrics
        train_mse = mean_squared_error(y_train, train_preds)
        train_rmse = sqrt(train_mse)
        train_mae = mean_absolute_error(y_train, train_preds)
        train_r2 = r2_score(y_train, train_preds)
        
        # Test metrics
        test_mse = mean_squared_error(y_test, test_preds)
        test_rmse = sqrt(test_mse)
        test_mae = mean_absolute_error(y_test, test_preds)
        test_r2 = r2_score(y_test, test_preds)
        
        return {
            'train_rmse': train_rmse,
            'train_mae': train_mae,
            'train_r2': train_r2,
            'test_rmse': test_rmse,
            'test_mae': test_mae,
            'test_r2': test_r2
        }
        
    except Exception as e:
        logger.error(f"Error calculating metrics: {str(e)}")
        raise


def _save_model(model: Any, model_path: str) -> None:
    """
    Save the trained model to disk.
    
    Args:
        model: Trained model object
        model_path: Path where to save the model
        
    Raises:
        Exception: If model saving fails
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        # Save the model
        joblib.dump(model, model_path)
        logger.info(f"Model saved successfully to {model_path}")
        
    except Exception as e:
        logger.error(f"Error saving model: {str(e)}")
        raise


def load_model(model_path: str = "src/model.pkl") -> Any:
    """
    Load a previously trained model from disk.
    
    Args:
        model_path: Path to the saved model file
        
    Returns:
        Loaded model object
        
    Raises:
        FileNotFoundError: If model file doesn't exist
        Exception: If model loading fails
    """
    try:
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
            
        model = joblib.load(model_path)
        logger.info(f"Model loaded successfully from {model_path}")
        
        return model
        
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        raise
