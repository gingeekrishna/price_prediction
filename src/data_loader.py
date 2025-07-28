"""
Data Loading and Processing Module

This module provides functionality for loading, processing, and merging
historical vehicle data with market trends data for price prediction.
"""

import os
import logging
from typing import Optional, Dict, Any
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_historical_data(path: str = "data/historical_vehicle_data.csv") -> pd.DataFrame:
    """
    Load historical vehicle data from CSV file.
    
    This function loads vehicle data including features like age, mileage,
    brand, model, and historical prices.
    
    Args:
        path: Path to the historical vehicle data CSV file
        
    Returns:
        pandas.DataFrame: Loaded historical vehicle data
        
    Raises:
        FileNotFoundError: If the data file doesn't exist
        Exception: If data loading fails
    """
    try:
        logger.info(f"Loading historical data from: {path}")
        
        if not os.path.exists(path):
            raise FileNotFoundError(f"Historical data file not found: {path}")
        
        # Load the CSV file
        df = pd.read_csv(path)
        
        # Validate the loaded data
        if df.empty:
            raise ValueError("Historical data file is empty")
        
        logger.info(f"Successfully loaded historical data: {df.shape[0]} rows, {df.shape[1]} columns")
        logger.debug(f"Columns: {df.columns.tolist()}")
        
        # Basic data quality checks
        _validate_historical_data(df)
        
        return df
        
    except Exception as e:
        logger.error(f"Error loading historical data: {str(e)}")
        raise


def load_market_data(path: str = "data/market_trends.csv") -> pd.DataFrame:
    """
    Load market trends data from CSV file or API.
    
    In a production environment, this would typically fetch data from
    a market data API using secure credentials. For now, it loads from CSV.
    
    Args:
        path: Path to the market trends CSV file
        
    Returns:
        pandas.DataFrame: Loaded market trends data
        
    Raises:
        FileNotFoundError: If the data file doesn't exist
        Exception: If data loading fails
    """
    try:
        logger.info(f"Loading market data from: {path}")
        
        # Get API key from environment (for future API integration)
        api_key = os.getenv("MARKET_API_KEY")
        if api_key:
            logger.info("Market API key found in environment")
            # TODO: Implement API call to fetch real-time market data
            # market_df = _fetch_market_data_from_api(api_key)
        
        if not os.path.exists(path):
            raise FileNotFoundError(f"Market data file not found: {path}")
        
        # Load the CSV file
        df = pd.read_csv(path)
        
        # Validate the loaded data
        if df.empty:
            raise ValueError("Market data file is empty")
        
        logger.info(f"Successfully loaded market data: {df.shape[0]} rows, {df.shape[1]} columns")
        logger.debug(f"Columns: {df.columns.tolist()}")
        
        # Basic data quality checks
        _validate_market_data(df)
        
        return df
        
    except Exception as e:
        logger.error(f"Error loading market data: {str(e)}")
        raise


def merge_data(
    hist_path: str = "data/historical_vehicle_data.csv",
    market_path: str = "data/market_trends.csv",
    merge_key: str = "date",
    how: str = "left"
) -> pd.DataFrame:
    """
    Merge historical vehicle data with market trends data.
    
    This function combines vehicle-specific data with market conditions
    to create a comprehensive dataset for price prediction.
    
    Args:
        hist_path: Path to historical vehicle data file
        market_path: Path to market trends data file
        merge_key: Column name to merge on (default: "date")
        how: Type of merge to perform (default: "left")
        
    Returns:
        pandas.DataFrame: Merged dataset ready for model training
        
    Raises:
        Exception: If merging fails
    """
    try:
        logger.info("Starting data merge process")
        
        # Get the project root directory (parent of src directory)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        
        # Convert relative paths to absolute paths
        if not os.path.isabs(hist_path):
            hist_path = os.path.join(project_root, hist_path)
        if not os.path.isabs(market_path):
            market_path = os.path.join(project_root, market_path)
        
        # Load both datasets
        hist_df = load_historical_data(hist_path)
        market_df = load_market_data(market_path)
        
        # Validate merge key exists in both datasets
        if merge_key not in hist_df.columns:
            raise ValueError(f"Merge key '{merge_key}' not found in historical data")
        if merge_key not in market_df.columns:
            raise ValueError(f"Merge key '{merge_key}' not found in market data")
        
        # Perform the merge
        logger.info(f"Merging data on '{merge_key}' column using '{how}' join")
        merged_df = pd.merge(hist_df, market_df, on=merge_key, how=how, suffixes=('', '_market'))
        
        # Validate merged result
        if merged_df.empty:
            raise ValueError("Merged dataset is empty - check if merge key values align")
        
        logger.info(f"Successfully merged data: {merged_df.shape[0]} rows, {merged_df.shape[1]} columns")
        
        # Handle missing values after merge
        merged_df = _handle_missing_values(merged_df)
        
        # Final validation
        _validate_merged_data(merged_df)
        
        return merged_df
        
    except Exception as e:
        logger.error(f"Error merging data: {str(e)}")
        raise


def _validate_historical_data(df: pd.DataFrame) -> None:
    """
    Validate historical vehicle data for common issues.
    
    Args:
        df: Historical vehicle DataFrame to validate
        
    Raises:
        ValueError: If critical validation checks fail
    """
    try:
        # Check for required columns
        required_cols = ['price']  # Minimum requirement
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Check for negative prices
        if 'price' in df.columns and (df['price'] < 0).any():
            logger.warning("Negative prices detected in historical data")
        
        # Check data types
        if 'date' in df.columns:
            try:
                pd.to_datetime(df['date'])
            except:
                logger.warning("Date column may not be in proper datetime format")
        
        logger.debug("Historical data validation completed")
        
    except Exception as e:
        logger.error(f"Historical data validation failed: {str(e)}")
        raise


def _validate_market_data(df: pd.DataFrame) -> None:
    """
    Validate market trends data for common issues.
    
    Args:
        df: Market trends DataFrame to validate
        
    Raises:
        ValueError: If critical validation checks fail
    """
    try:
        # Check data types
        if 'date' in df.columns:
            try:
                pd.to_datetime(df['date'])
            except:
                logger.warning("Date column may not be in proper datetime format")
        
        # Check for reasonable market index values
        if 'market_index' in df.columns:
            market_values = df['market_index']
            if (market_values < 0).any():
                logger.warning("Negative market index values detected")
        
        logger.debug("Market data validation completed")
        
    except Exception as e:
        logger.error(f"Market data validation failed: {str(e)}")
        raise


def _validate_merged_data(df: pd.DataFrame) -> None:
    """
    Validate merged dataset for modeling readiness.
    
    Args:
        df: Merged DataFrame to validate
        
    Raises:
        ValueError: If critical validation checks fail
    """
    try:
        # Check for target column
        if 'price' not in df.columns:
            raise ValueError("Target column 'price' missing from merged data")
        
        # Check for sufficient data (reduced to 3 for demo purposes)
        if len(df) < 3:
            raise ValueError("Insufficient data for modeling (minimum 3 samples required)")
        
        # Report missing value summary
        missing_summary = df.isnull().sum()
        if missing_summary.sum() > 0:
            logger.info("Missing values summary:")
            for col, count in missing_summary[missing_summary > 0].items():
                logger.info(f"  {col}: {count} missing values")
        
        logger.debug("Merged data validation completed")
        
    except Exception as e:
        logger.error(f"Merged data validation failed: {str(e)}")
        raise


def _handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle missing values in the merged dataset.
    
    Args:
        df: DataFrame with potential missing values
        
    Returns:
        pandas.DataFrame: DataFrame with missing values handled
    """
    try:
        logger.info("Handling missing values in merged dataset")
        
        # Forward fill for time series data
        if 'date' in df.columns:
            df = df.sort_values('date')
            df = df.fillna(method='ffill')
        
        # Fill remaining missing values with appropriate defaults
        numeric_columns = df.select_dtypes(include=['number']).columns
        df[numeric_columns] = df[numeric_columns].fillna(0)
        
        # Fill categorical columns with 'unknown'
        categorical_columns = df.select_dtypes(include=['object']).columns
        df[categorical_columns] = df[categorical_columns].fillna('unknown')
        
        logger.info("Missing values handled successfully")
        return df
        
    except Exception as e:
        logger.error(f"Error handling missing values: {str(e)}")
        raise


def get_data_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate a comprehensive summary of the dataset.
    
    Args:
        df: DataFrame to summarize
        
    Returns:
        Dictionary containing dataset summary statistics
    """
    try:
        summary = {
            'shape': df.shape,
            'columns': df.columns.tolist(),
            'dtypes': df.dtypes.to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'numeric_summary': df.describe().to_dict() if len(df.select_dtypes(include=['number']).columns) > 0 else {}
        }
        
        logger.info(f"Generated summary for dataset: {summary['shape']}")
        return summary
        
    except Exception as e:
        logger.error(f"Error generating data summary: {str(e)}")
        raise
