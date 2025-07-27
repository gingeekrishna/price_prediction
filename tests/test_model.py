"""
Unit tests for the model training and evaluation module.

This module contains comprehensive tests for model training,
evaluation, saving, and loading functionality.
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

from model import train_model, load_model, _calculate_metrics, _save_model


class TestModelTraining:
    """Test suite for model training functionality."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample training data for testing."""
        np.random.seed(42)
        n_samples = 100
        
        data = {
            'age': np.random.randint(1, 15, n_samples),
            'mileage': np.random.randint(10000, 200000, n_samples),
            'market_index': np.random.uniform(1000, 1200, n_samples),
            'fuel_price': np.random.uniform(3.0, 4.5, n_samples),
            'date': pd.date_range('2020-01-01', periods=n_samples, freq='D'),
            'price': np.random.uniform(15000, 35000, n_samples)
        }
        
        return pd.DataFrame(data)
    
    @pytest.fixture
    def minimal_data(self):
        """Create minimal valid training data."""
        return pd.DataFrame({
            'age': [1, 2, 3, 4, 5],
            'mileage': [10000, 20000, 30000, 40000, 50000],
            'price': [30000, 25000, 20000, 18000, 15000]
        })
    
    def test_train_model_success(self, sample_data):
        """Test successful model training with valid data."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as tmp_file:
            model_path = tmp_file.name
        
        try:
            model, metrics = train_model(
                sample_data, 
                target="price",
                save_model=True,
                model_path=model_path
            )
            
            # Check model is returned
            assert model is not None
            assert hasattr(model, 'predict')
            assert hasattr(model, 'fit')
            
            # Check metrics are returned
            assert isinstance(metrics, dict)
            required_metrics = ['train_rmse', 'test_rmse', 'train_r2', 'test_r2', 'train_mae', 'test_mae']
            for metric in required_metrics:
                assert metric in metrics
                assert isinstance(metrics[metric], (int, float))
            
            # Check model file was saved
            assert os.path.exists(model_path)
            
        finally:
            # Cleanup
            if os.path.exists(model_path):
                os.unlink(model_path)
    
    def test_train_model_with_minimal_data(self, minimal_data):
        """Test model training with minimal valid data."""
        model, metrics = train_model(minimal_data, target="price", save_model=False)
        
        assert model is not None
        assert isinstance(metrics, dict)
        assert metrics['test_rmse'] >= 0
    
    def test_train_model_none_dataframe(self):
        """Test training with None DataFrame raises ValueError."""
        with pytest.raises(ValueError, match="DataFrame cannot be None or empty"):
            train_model(None)
    
    def test_train_model_empty_dataframe(self):
        """Test training with empty DataFrame raises ValueError."""
        empty_df = pd.DataFrame()
        with pytest.raises(ValueError, match="DataFrame cannot be None or empty"):
            train_model(empty_df)
    
    def test_train_model_missing_target(self, sample_data):
        """Test training with missing target column raises ValueError."""
        with pytest.raises(ValueError, match="Target column 'nonexistent' not found"):
            train_model(sample_data, target="nonexistent")
    
    def test_train_model_insufficient_data(self):
        """Test training with insufficient data raises ValueError."""
        small_df = pd.DataFrame({
            'age': [1, 2],
            'price': [20000, 25000]
        })
        
        with pytest.raises(ValueError, match="Insufficient data for training"):
            train_model(small_df)
    
    def test_train_model_with_missing_values(self):
        """Test training handles missing values appropriately."""
        data_with_missing = pd.DataFrame({
            'age': [1, 2, np.nan, 4, 5, 6, 7, 8, 9, 10],
            'mileage': [10000, np.nan, 30000, 40000, 50000, 60000, 70000, 80000, 90000, 100000],
            'price': [30000, 25000, 20000, 18000, 15000, 14000, 13000, 12000, 11000, 10000]
        })
        
        model, metrics = train_model(data_with_missing, save_model=False)
        
        assert model is not None
        assert isinstance(metrics, dict)
    
    def test_train_model_with_missing_target_values(self):
        """Test training handles missing target values by removing rows."""
        data_with_missing_target = pd.DataFrame({
            'age': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'mileage': [10000, 20000, 30000, 40000, 50000, 60000, 70000, 80000, 90000, 100000],
            'price': [30000, np.nan, 20000, 18000, np.nan, 14000, 13000, 12000, 11000, 10000]
        })
        
        model, metrics = train_model(data_with_missing_target, save_model=False)
        
        assert model is not None
        assert isinstance(metrics, dict)
    
    def test_train_model_custom_parameters(self, sample_data):
        """Test training with custom parameters."""
        model, metrics = train_model(
            sample_data,
            target="price",
            test_size=0.3,
            random_state=123,
            n_estimators=50,
            save_model=False
        )
        
        assert model is not None
        assert model.n_estimators == 50
        assert isinstance(metrics, dict)
    
    @patch('model.logger')
    def test_train_model_logging(self, mock_logger, sample_data):
        """Test that appropriate logging occurs during training."""
        train_model(sample_data, save_model=False)
        
        # Verify that info logs were called
        mock_logger.info.assert_called()
        
        # Check for specific log messages
        log_calls = [call[0][0] for call in mock_logger.info.call_args_list]
        assert any("Starting model training process" in call for call in log_calls)
        assert any("Model training completed successfully" in call for call in log_calls)


class TestModelSaveLoad:
    """Test suite for model saving and loading functionality."""
    
    def test_save_model_success(self):
        """Test successful model saving."""
        # Create a mock model
        mock_model = Mock()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as tmp_file:
            model_path = tmp_file.name
        
        try:
            with patch('model.joblib.dump') as mock_dump:
                _save_model(mock_model, model_path)
                mock_dump.assert_called_once_with(mock_model, model_path)
        
        finally:
            if os.path.exists(model_path):
                os.unlink(model_path)
    
    def test_save_model_creates_directory(self):
        """Test that save_model creates directory if it doesn't exist."""
        mock_model = Mock()
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            nested_path = os.path.join(tmp_dir, 'nested', 'path', 'model.pkl')
            
            with patch('model.joblib.dump') as mock_dump:
                _save_model(mock_model, nested_path)
                
                # Verify directory was created
                assert os.path.exists(os.path.dirname(nested_path))
                mock_dump.assert_called_once()
    
    def test_load_model_success(self):
        """Test successful model loading."""
        mock_model = Mock()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as tmp_file:
            model_path = tmp_file.name
        
        try:
            with patch('model.joblib.load', return_value=mock_model) as mock_load:
                result = load_model(model_path)
                
                assert result == mock_model
                mock_load.assert_called_once_with(model_path)
        
        finally:
            if os.path.exists(model_path):
                os.unlink(model_path)
    
    def test_load_model_file_not_found(self):
        """Test loading model when file doesn't exist raises FileNotFoundError."""
        non_existent_path = "/path/that/does/not/exist/model.pkl"
        
        with pytest.raises(FileNotFoundError, match="Model file not found"):
            load_model(non_existent_path)
    
    def test_load_model_loading_error(self):
        """Test model loading handles joblib errors."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as tmp_file:
            model_path = tmp_file.name
        
        try:
            with patch('model.joblib.load', side_effect=Exception("Loading error")):
                with pytest.raises(Exception, match="Loading error"):
                    load_model(model_path)
        
        finally:
            if os.path.exists(model_path):
                os.unlink(model_path)


class TestCalculateMetrics:
    """Test suite for metrics calculation functionality."""
    
    def test_calculate_metrics_success(self):
        """Test successful metrics calculation."""
        # Create sample predictions and actual values
        y_train = pd.Series([1000, 2000, 3000, 4000, 5000])
        train_preds = np.array([1100, 1900, 3100, 3900, 5100])
        y_test = pd.Series([1500, 2500, 3500])
        test_preds = np.array([1400, 2600, 3400])
        
        metrics = _calculate_metrics(y_train, train_preds, y_test, test_preds)
        
        assert isinstance(metrics, dict)
        
        required_metrics = ['train_rmse', 'test_rmse', 'train_r2', 'test_r2', 'train_mae', 'test_mae']
        for metric in required_metrics:
            assert metric in metrics
            assert isinstance(metrics[metric], (int, float))
            assert metrics[metric] >= 0 or 'r2' in metric  # R² can be negative
    
    def test_calculate_metrics_perfect_predictions(self):
        """Test metrics calculation with perfect predictions."""
        y_train = pd.Series([1000, 2000, 3000])
        train_preds = np.array([1000, 2000, 3000])  # Perfect predictions
        y_test = pd.Series([1500, 2500])
        test_preds = np.array([1500, 2500])  # Perfect predictions
        
        metrics = _calculate_metrics(y_train, train_preds, y_test, test_preds)
        
        # Perfect predictions should have RMSE = 0, MAE = 0, R² = 1
        assert metrics['train_rmse'] == 0
        assert metrics['test_rmse'] == 0
        assert metrics['train_mae'] == 0
        assert metrics['test_mae'] == 0
        assert metrics['train_r2'] == 1.0
        assert metrics['test_r2'] == 1.0
    
    def test_calculate_metrics_error_handling(self):
        """Test metrics calculation handles errors appropriately."""
        # Test with mismatched array sizes
        y_train = pd.Series([1000, 2000])
        train_preds = np.array([1100])  # Wrong size
        y_test = pd.Series([1500])
        test_preds = np.array([1400])
        
        with pytest.raises(Exception):
            _calculate_metrics(y_train, train_preds, y_test, test_preds)


class TestModelIntegration:
    """Integration tests for the complete model workflow."""
    
    def test_full_model_workflow(self):
        """Test complete model training, saving, and loading workflow."""
        # Create sample data
        np.random.seed(42)
        data = pd.DataFrame({
            'age': np.random.randint(1, 10, 20),
            'mileage': np.random.randint(10000, 100000, 20),
            'price': np.random.uniform(15000, 35000, 20)
        })
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as tmp_file:
            model_path = tmp_file.name
        
        try:
            # Train and save model
            trained_model, metrics = train_model(
                data, 
                target="price",
                save_model=True,
                model_path=model_path
            )
            
            # Load saved model
            loaded_model = load_model(model_path)
            
            # Test that loaded model works
            test_input = data[['age', 'mileage']].iloc[:1]
            prediction1 = trained_model.predict(test_input)
            prediction2 = loaded_model.predict(test_input)
            
            # Predictions should be identical
            np.testing.assert_array_almost_equal(prediction1, prediction2)
            
        finally:
            if os.path.exists(model_path):
                os.unlink(model_path)


if __name__ == '__main__':
    pytest.main([__file__])
