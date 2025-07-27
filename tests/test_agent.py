"""
Unit tests for the VehiclePriceAgent class.

This module contains comprehensive tests for the agent's
perceive-decide-act functionality and error handling.
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agent import VehiclePriceAgent


class TestVehiclePriceAgent:
    """Test suite for VehiclePriceAgent class."""
    
    @pytest.fixture
    def mock_model(self):
        """Create a mock model for testing."""
        model = Mock()
        model.predict.return_value = np.array([25000.0])
        model.feature_names_in_ = ['age', 'mileage', 'market_index']
        return model
    
    @pytest.fixture
    def feature_names(self):
        """Standard feature names for testing."""
        return ['age', 'mileage', 'market_index']
    
    @pytest.fixture
    def agent(self, mock_model, feature_names):
        """Create a VehiclePriceAgent instance for testing."""
        return VehiclePriceAgent(mock_model, feature_names)
    
    @pytest.fixture
    def sample_vehicle_data(self):
        """Sample vehicle data for testing."""
        return {
            'age': 3,
            'mileage': 45000,
            'brand': 'Toyota'
        }
    
    @pytest.fixture
    def sample_market_data(self):
        """Sample market data for testing."""
        return {
            'market_index': 1100.5,
            'fuel_price': 3.75
        }
    
    def test_agent_initialization_success(self, mock_model, feature_names):
        """Test successful agent initialization."""
        agent = VehiclePriceAgent(mock_model, feature_names)
        assert agent.model == mock_model
        assert agent.feature_names == feature_names
    
    def test_agent_initialization_none_model(self, feature_names):
        """Test agent initialization with None model raises ValueError."""
        with pytest.raises(ValueError, match="Model cannot be None"):
            VehiclePriceAgent(None, feature_names)
    
    def test_agent_initialization_empty_features(self, mock_model):
        """Test agent initialization with empty features raises ValueError."""
        with pytest.raises(ValueError, match="Feature names cannot be empty"):
            VehiclePriceAgent(mock_model, [])
    
    def test_perceive_success(self, agent, sample_vehicle_data, sample_market_data):
        """Test successful data perception and processing."""
        result = agent.perceive(sample_vehicle_data, sample_market_data)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert 'age' in result.columns
        assert 'mileage' in result.columns
        assert 'market_index' in result.columns
        assert result.iloc[0]['age'] == 3
        assert result.iloc[0]['mileage'] == 45000
        assert result.iloc[0]['market_index'] == 1100.5
    
    def test_perceive_missing_features(self, agent):
        """Test perception with missing features fills with 0."""
        vehicle_data = {'age': 5}
        market_data = {}
        
        result = agent.perceive(vehicle_data, market_data)
        
        assert result.iloc[0]['age'] == 5
        assert result.iloc[0]['mileage'] == 0  # Missing feature filled with 0
        assert result.iloc[0]['market_index'] == 0  # Missing feature filled with 0
    
    def test_perceive_invalid_input_types(self, agent):
        """Test perception with invalid input types raises ValueError."""
        with pytest.raises(ValueError, match="Input data must be dictionaries"):
            agent.perceive("invalid", {})
        
        with pytest.raises(ValueError, match="Input data must be dictionaries"):
            agent.perceive({}, "invalid")
    
    def test_decide_success(self, agent):
        """Test successful prediction decision."""
        input_data = pd.DataFrame([{'age': 3, 'mileage': 45000, 'market_index': 1100.5}])
        
        result = agent.decide(input_data)
        
        assert isinstance(result, float)
        assert result == 25000.0
        agent.model.predict.assert_called_once()
    
    def test_decide_invalid_prediction_type(self, agent):
        """Test decision with invalid prediction type."""
        input_data = pd.DataFrame([{'age': 3, 'mileage': 45000, 'market_index': 1100.5}])
        agent.model.predict.return_value = ["invalid"]
        
        with pytest.raises(ValueError, match="Invalid prediction type"):
            agent.decide(input_data)
    
    def test_decide_negative_prediction_warning(self, agent, caplog):
        """Test warning for negative predictions."""
        input_data = pd.DataFrame([{'age': 3, 'mileage': 45000, 'market_index': 1100.5}])
        agent.model.predict.return_value = np.array([-5000.0])
        
        result = agent.decide(input_data)
        
        assert result == -5000.0
        assert "Negative prediction detected" in caplog.text
    
    def test_act_success(self, agent):
        """Test successful action formatting."""
        prediction = 25000.0
        
        result = agent.act(prediction)
        
        assert result == "Recommended price: $25,000.00"
    
    def test_act_invalid_prediction_type(self, agent):
        """Test action with invalid prediction type raises ValueError."""
        with pytest.raises(ValueError, match="Prediction must be numeric"):
            agent.act("invalid")
    
    def test_run_complete_cycle(self, agent, sample_vehicle_data, sample_market_data):
        """Test complete perception-decision-action cycle."""
        result = agent.run(sample_vehicle_data, sample_market_data)
        
        assert isinstance(result, str)
        assert "Recommended price: $25,000.00" == result
        agent.model.predict.assert_called_once()
    
    def test_run_with_exception_in_perceive(self, agent):
        """Test run method handles exceptions in perceive phase."""
        with pytest.raises(ValueError):
            agent.run("invalid", {})
    
    def test_run_with_exception_in_decide(self, agent, sample_vehicle_data, sample_market_data):
        """Test run method handles exceptions in decide phase."""
        agent.model.predict.side_effect = Exception("Model error")
        
        with pytest.raises(Exception, match="Model error"):
            agent.run(sample_vehicle_data, sample_market_data)
    
    @patch('agent.logger')
    def test_logging_behavior(self, mock_logger, agent, sample_vehicle_data, sample_market_data):
        """Test that appropriate logging occurs during operations."""
        agent.run(sample_vehicle_data, sample_market_data)
        
        # Verify that info logs were called
        mock_logger.info.assert_called()
        
        # Check that specific log messages were generated
        log_calls = [call[0][0] for call in mock_logger.info.call_args_list]
        assert any("Starting price prediction cycle" in call for call in log_calls)
        assert any("Price prediction cycle completed successfully" in call for call in log_calls)


class TestVehiclePriceAgentIntegration:
    """Integration tests for VehiclePriceAgent with real-like scenarios."""
    
    def test_end_to_end_prediction_scenario(self):
        """Test end-to-end prediction with realistic data."""
        # Create a simple mock model
        model = Mock()
        model.predict.return_value = np.array([22500.0])
        model.feature_names_in_ = ['age', 'mileage', 'market_index', 'fuel_price']
        
        # Create agent
        feature_names = ['age', 'mileage', 'market_index', 'fuel_price']
        agent = VehiclePriceAgent(model, feature_names)
        
        # Realistic vehicle data
        vehicle_data = {
            'age': 2,
            'mileage': 25000,
            'brand': 'Honda',
            'model': 'Civic'
        }
        
        # Realistic market data
        market_data = {
            'market_index': 1150.0,
            'fuel_price': 3.85,
            'economic_indicator': 0.95
        }
        
        # Run prediction
        result = agent.run(vehicle_data, market_data)
        
        # Verify result
        assert "Recommended price: $22,500.00" == result
        
        # Verify model was called with correct data structure
        model.predict.assert_called_once()
        call_args = model.predict.call_args[0][0]
        assert isinstance(call_args, pd.DataFrame)
        assert len(call_args) == 1
        assert call_args.iloc[0]['age'] == 2
        assert call_args.iloc[0]['mileage'] == 25000
        assert call_args.iloc[0]['market_index'] == 1150.0
        assert call_args.iloc[0]['fuel_price'] == 3.85


if __name__ == '__main__':
    pytest.main([__file__])
