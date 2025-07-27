"""
Unit tests for the data loading and processing module.

This module contains comprehensive tests for data loading,
validation, merging, and preprocessing functionality.
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, mock_open, Mock
import tempfile
import os
import sys

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_loader import (
    load_historical_data, 
    load_market_data, 
    merge_data,
    get_data_summary,
    _validate_historical_data,
    _validate_market_data,
    _validate_merged_data,
    _handle_missing_values
)


class TestDataLoading:
    """Test suite for data loading functionality."""
    
    @pytest.fixture
    def sample_historical_csv_content(self):
        """Sample CSV content for historical data."""
        return """date,age,mileage,brand,model,price
2023-01-01,3,45000,Toyota,Camry,25000
2023-01-02,5,75000,Honda,Civic,18000
2023-01-03,2,30000,Ford,Focus,22000
2023-01-04,7,95000,Toyota,Corolla,15000"""
    
    @pytest.fixture
    def sample_market_csv_content(self):
        """Sample CSV content for market data."""
        return """date,market_index,fuel_price,economic_indicator
2023-01-01,1100.5,3.75,0.95
2023-01-02,1105.2,3.78,0.96
2023-01-03,1098.7,3.73,0.94
2023-01-04,1102.1,3.76,0.95"""
    
    def test_load_historical_data_success(self, sample_historical_csv_content):
        """Test successful loading of historical data."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tmp_file:
            tmp_file.write(sample_historical_csv_content)
            tmp_file.flush()
            
            try:
                df = load_historical_data(tmp_file.name)
                
                assert isinstance(df, pd.DataFrame)
                assert len(df) == 4
                assert 'price' in df.columns
                assert 'age' in df.columns
                assert 'date' in df.columns
                assert df.iloc[0]['brand'] == 'Toyota'
                
            finally:
                os.unlink(tmp_file.name)
    
    def test_load_historical_data_file_not_found(self):
        """Test loading historical data when file doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Historical data file not found"):
            load_historical_data("/nonexistent/path/data.csv")
    
    def test_load_historical_data_empty_file(self):
        """Test loading historical data from empty file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tmp_file:
            tmp_file.write("")  # Empty file
            tmp_file.flush()
            
            try:
                with pytest.raises(ValueError, match="Historical data file is empty"):
                    load_historical_data(tmp_file.name)
            finally:
                os.unlink(tmp_file.name)
    
    def test_load_market_data_success(self, sample_market_csv_content):
        """Test successful loading of market data."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tmp_file:
            tmp_file.write(sample_market_csv_content)
            tmp_file.flush()
            
            try:
                df = load_market_data(tmp_file.name)
                
                assert isinstance(df, pd.DataFrame)
                assert len(df) == 4
                assert 'market_index' in df.columns
                assert 'fuel_price' in df.columns
                assert 'date' in df.columns
                assert df.iloc[0]['market_index'] == 1100.5
                
            finally:
                os.unlink(tmp_file.name)
    
    def test_load_market_data_file_not_found(self):
        """Test loading market data when file doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Market data file not found"):
            load_market_data("/nonexistent/path/data.csv")
    
    @patch.dict(os.environ, {'MARKET_API_KEY': 'test_api_key'})
    def test_load_market_data_with_api_key(self, sample_market_csv_content):
        """Test market data loading logs API key presence."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tmp_file:
            tmp_file.write(sample_market_csv_content)
            tmp_file.flush()
            
            try:
                with patch('data_loader.logger') as mock_logger:
                    load_market_data(tmp_file.name)
                    
                    # Check that API key presence was logged
                    log_calls = [call[0][0] for call in mock_logger.info.call_args_list]
                    assert any("Market API key found" in call for call in log_calls)
                    
            finally:
                os.unlink(tmp_file.name)


class TestDataMerging:
    """Test suite for data merging functionality."""
    
    @pytest.fixture
    def historical_df(self):
        """Sample historical DataFrame."""
        return pd.DataFrame({
            'date': ['2023-01-01', '2023-01-02', '2023-01-03'],
            'age': [3, 5, 2],
            'mileage': [45000, 75000, 30000],
            'price': [25000, 18000, 22000]
        })
    
    @pytest.fixture
    def market_df(self):
        """Sample market DataFrame."""
        return pd.DataFrame({
            'date': ['2023-01-01', '2023-01-02', '2023-01-03'],
            'market_index': [1100.5, 1105.2, 1098.7],
            'fuel_price': [3.75, 3.78, 3.73]
        })
    
    def test_merge_data_success(self, historical_df, market_df):
        """Test successful data merging."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as hist_file:
            historical_df.to_csv(hist_file.name, index=False)
            
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as market_file:
                market_df.to_csv(market_file.name, index=False)
                
                try:
                    merged_df = merge_data(hist_file.name, market_file.name)
                    
                    assert isinstance(merged_df, pd.DataFrame)
                    assert len(merged_df) == 3
                    assert 'price' in merged_df.columns
                    assert 'market_index' in merged_df.columns
                    assert 'fuel_price' in merged_df.columns
                    assert merged_df.iloc[0]['age'] == 3
                    assert merged_df.iloc[0]['market_index'] == 1100.5
                    
                finally:
                    os.unlink(hist_file.name)
                    os.unlink(market_file.name)
    
    def test_merge_data_missing_merge_key(self):
        """Test merging when merge key is missing."""
        hist_df = pd.DataFrame({
            'timestamp': ['2023-01-01'],  # Different key name
            'age': [3],
            'price': [25000]
        })
        
        market_df = pd.DataFrame({
            'date': ['2023-01-01'],
            'market_index': [1100.5]
        })
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as hist_file:
            hist_df.to_csv(hist_file.name, index=False)
            
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as market_file:
                market_df.to_csv(market_file.name, index=False)
                
                try:
                    with pytest.raises(ValueError, match="Merge key 'date' not found in historical data"):
                        merge_data(hist_file.name, market_file.name, merge_key="date")
                        
                finally:
                    os.unlink(hist_file.name)
                    os.unlink(market_file.name)
    
    def test_merge_data_empty_result(self):
        """Test merging when result is empty."""
        hist_df = pd.DataFrame({
            'date': ['2023-01-01'],
            'age': [3],
            'price': [25000]
        })
        
        market_df = pd.DataFrame({
            'date': ['2023-02-01'],  # No matching dates
            'market_index': [1100.5]
        })
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as hist_file:
            hist_df.to_csv(hist_file.name, index=False)
            
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as market_file:
                market_df.to_csv(market_file.name, index=False)
                
                try:
                    with pytest.raises(ValueError, match="Merged dataset is empty"):
                        merge_data(hist_file.name, market_file.name, how="inner")
                        
                finally:
                    os.unlink(hist_file.name)
                    os.unlink(market_file.name)


class TestDataValidation:
    """Test suite for data validation functionality."""
    
    def test_validate_historical_data_success(self):
        """Test successful historical data validation."""
        valid_df = pd.DataFrame({
            'date': ['2023-01-01', '2023-01-02'],
            'age': [3, 5],
            'price': [25000, 18000]
        })
        
        # Should not raise any exceptions
        _validate_historical_data(valid_df)
    
    def test_validate_historical_data_missing_price(self):
        """Test validation fails when price column is missing."""
        invalid_df = pd.DataFrame({
            'date': ['2023-01-01'],
            'age': [3]
            # Missing price column
        })
        
        with pytest.raises(ValueError, match="Missing required columns"):
            _validate_historical_data(invalid_df)
    
    def test_validate_historical_data_negative_prices(self):
        """Test validation warns about negative prices."""
        df_with_negative = pd.DataFrame({
            'date': ['2023-01-01', '2023-01-02'],
            'age': [3, 5],
            'price': [25000, -5000]  # Negative price
        })
        
        with patch('data_loader.logger') as mock_logger:
            _validate_historical_data(df_with_negative)
            
            # Check that warning was logged
            log_calls = [call[0][0] for call in mock_logger.warning.call_args_list]
            assert any("Negative prices detected" in call for call in log_calls)
    
    def test_validate_market_data_success(self):
        """Test successful market data validation."""
        valid_df = pd.DataFrame({
            'date': ['2023-01-01', '2023-01-02'],
            'market_index': [1100.5, 1105.2],
            'fuel_price': [3.75, 3.78]
        })
        
        # Should not raise any exceptions
        _validate_market_data(valid_df)
    
    def test_validate_market_data_negative_index(self):
        """Test validation warns about negative market index."""
        df_with_negative = pd.DataFrame({
            'date': ['2023-01-01'],
            'market_index': [-100.0],  # Negative market index
            'fuel_price': [3.75]
        })
        
        with patch('data_loader.logger') as mock_logger:
            _validate_market_data(df_with_negative)
            
            # Check that warning was logged
            log_calls = [call[0][0] for call in mock_logger.warning.call_args_list]
            assert any("Negative market index values detected" in call for call in log_calls)
    
    def test_validate_merged_data_success(self):
        """Test successful merged data validation."""
        valid_df = pd.DataFrame({
            'date': ['2023-01-01', '2023-01-02'],
            'age': [3, 5],
            'price': [25000, 18000],
            'market_index': [1100.5, 1105.2]
        })
        
        # Should not raise any exceptions
        _validate_merged_data(valid_df)
    
    def test_validate_merged_data_missing_price(self):
        """Test validation fails when price column is missing from merged data."""
        invalid_df = pd.DataFrame({
            'date': ['2023-01-01'],
            'age': [3],
            'market_index': [1100.5]
            # Missing price column
        })
        
        with pytest.raises(ValueError, match="Target column 'price' missing"):
            _validate_merged_data(invalid_df)
    
    def test_validate_merged_data_insufficient_data(self):
        """Test validation fails with insufficient data."""
        small_df = pd.DataFrame({
            'price': [25000],
            'age': [3]
        })
        
        with pytest.raises(ValueError, match="Insufficient data for modeling"):
            _validate_merged_data(small_df)


class TestMissingValueHandling:
    """Test suite for missing value handling functionality."""
    
    def test_handle_missing_values_numeric(self):
        """Test missing value handling for numeric columns."""
        df_with_missing = pd.DataFrame({
            'age': [3, np.nan, 5],
            'price': [25000, 18000, np.nan],
            'market_index': [1100.5, 1105.2, 1098.7]
        })
        
        result = _handle_missing_values(df_with_missing)
        
        assert not result.isnull().any().any()  # No missing values remain
        assert result.iloc[1]['age'] == 0  # Filled with 0
        assert result.iloc[2]['price'] == 0  # Filled with 0
    
    def test_handle_missing_values_categorical(self):
        """Test missing value handling for categorical columns."""
        df_with_missing = pd.DataFrame({
            'brand': ['Toyota', np.nan, 'Honda'],
            'model': ['Camry', 'Civic', np.nan],
            'price': [25000, 18000, 22000]
        })
        
        result = _handle_missing_values(df_with_missing)
        
        assert not result.isnull().any().any()  # No missing values remain
        assert result.iloc[1]['brand'] == 'unknown'  # Filled with 'unknown'
        assert result.iloc[2]['model'] == 'unknown'  # Filled with 'unknown'
    
    def test_handle_missing_values_with_date_column(self):
        """Test missing value handling with date column (forward fill)."""
        df_with_missing = pd.DataFrame({
            'date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03']),
            'age': [3, np.nan, 5],
            'price': [25000, np.nan, 22000]
        })
        
        result = _handle_missing_values(df_with_missing)
        
        assert not result.isnull().any().any()  # No missing values remain
        # Forward fill should propagate previous values
        assert result.iloc[1]['age'] == 3  # Forward filled
        assert result.iloc[1]['price'] == 25000  # Forward filled


class TestDataSummary:
    """Test suite for data summary functionality."""
    
    def test_get_data_summary_success(self):
        """Test successful data summary generation."""
        sample_df = pd.DataFrame({
            'age': [3, 5, 2, 7],
            'mileage': [45000, 75000, 30000, 95000],
            'price': [25000, 18000, 22000, 15000],
            'brand': ['Toyota', 'Honda', 'Ford', 'Toyota']
        })
        
        summary = get_data_summary(sample_df)
        
        assert isinstance(summary, dict)
        assert 'shape' in summary
        assert 'columns' in summary
        assert 'dtypes' in summary
        assert 'missing_values' in summary
        assert 'numeric_summary' in summary
        
        assert summary['shape'] == (4, 4)
        assert len(summary['columns']) == 4
        assert 'age' in summary['columns']
        assert 'price' in summary['columns']
    
    def test_get_data_summary_with_missing_values(self):
        """Test data summary with missing values."""
        df_with_missing = pd.DataFrame({
            'age': [3, np.nan, 5],
            'price': [25000, 18000, np.nan]
        })
        
        summary = get_data_summary(df_with_missing)
        
        assert summary['missing_values']['age'] == 1
        assert summary['missing_values']['price'] == 1
    
    def test_get_data_summary_empty_dataframe(self):
        """Test data summary with empty DataFrame."""
        empty_df = pd.DataFrame()
        
        summary = get_data_summary(empty_df)
        
        assert summary['shape'] == (0, 0)
        assert summary['columns'] == []


class TestDataLoaderIntegration:
    """Integration tests for the complete data loading workflow."""
    
    def test_full_data_pipeline(self):
        """Test complete data loading and merging pipeline."""
        # Create sample data files
        historical_data = """date,age,mileage,brand,price
2023-01-01,3,45000,Toyota,25000
2023-01-02,5,75000,Honda,18000
2023-01-03,2,30000,Ford,22000"""
        
        market_data = """date,market_index,fuel_price
2023-01-01,1100.5,3.75
2023-01-02,1105.2,3.78
2023-01-03,1098.7,3.73"""
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as hist_file:
            hist_file.write(historical_data)
            hist_file.flush()
            
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as market_file:
                market_file.write(market_data)
                market_file.flush()
                
                try:
                    # Test complete pipeline
                    merged_df = merge_data(hist_file.name, market_file.name)
                    summary = get_data_summary(merged_df)
                    
                    # Verify results
                    assert isinstance(merged_df, pd.DataFrame)
                    assert len(merged_df) == 3
                    assert 'price' in merged_df.columns
                    assert 'market_index' in merged_df.columns
                    assert 'fuel_price' in merged_df.columns
                    
                    assert isinstance(summary, dict)
                    assert summary['shape'] == (3, 5)  # 3 rows, 5 columns after merge
                    
                finally:
                    os.unlink(hist_file.name)
                    os.unlink(market_file.name)


if __name__ == '__main__':
    pytest.main([__file__])
