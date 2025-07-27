"""
Market Data Agent

This module contains the MarketAgent class responsible for collecting
and providing real-time market data for vehicle price predictions.
It simulates market conditions and can be extended to use real APIs.
"""

import logging
import random
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MarketAgent:
    """
    Agent responsible for collecting and providing market data.
    
    This agent simulates market conditions such as market indices,
    fuel prices, and economic indicators. In production, this would
    connect to real market data APIs.
    
    Attributes:
        api_key: API key for market data service (if using real API)
        cache_ttl: Time-to-live for cached market data (seconds)
        last_update: Timestamp of last data update
        cached_data: Cached market data
    """
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        cache_ttl: int = 3600,  # 1 hour cache
        use_simulation: bool = True
    ):
        """
        Initialize the Market Agent.
        
        Args:
            api_key: API key for market data service
            cache_ttl: Cache time-to-live in seconds
            use_simulation: Whether to use simulated data or real API
        """
        self.api_key = api_key or os.getenv('MARKET_API_KEY')
        self.cache_ttl = cache_ttl
        self.use_simulation = use_simulation
        self.last_update = None
        self.cached_data = None
        
        # Initialize random seed for consistent simulation
        random.seed(42)
        
        logger.info(f"Market Agent initialized (simulation: {use_simulation})")
        if self.api_key:
            logger.info("Market API key available for real data access")
    
    def get_market_data(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get current market data with caching support.
        
        Args:
            force_refresh: Whether to force refresh cached data
            
        Returns:
            Dictionary containing current market data
        """
        try:
            # Check if we can use cached data
            if not force_refresh and self._is_cache_valid():
                logger.debug("Using cached market data")
                return self.cached_data.copy()
            
            # Fetch fresh market data
            if self.use_simulation or not self.api_key:
                market_data = self._get_simulated_market_data()
            else:
                market_data = self._get_real_market_data()
            
            # Update cache
            self.cached_data = market_data
            self.last_update = datetime.now()
            
            logger.info("Market data updated successfully")
            return market_data.copy()
            
        except Exception as e:
            logger.error(f"Failed to get market data: {e}")
            
            # Return cached data if available, otherwise return default values
            if self.cached_data:
                logger.warning("Using stale cached data due to error")
                return self.cached_data.copy()
            else:
                logger.warning("Using default market data due to error")
                return self._get_default_market_data()
    
    def _get_simulated_market_data(self) -> Dict[str, Any]:
        """
        Generate simulated market data for testing and development.
        
        Returns:
            Dictionary containing simulated market conditions
        """
        try:
            # Base values with realistic ranges
            base_market_index = 1100.0
            base_fuel_price = 3.75
            base_economic_indicator = 0.95
            base_interest_rate = 5.5
            
            # Add realistic variations
            market_variation = random.uniform(-50, 50)
            fuel_variation = random.uniform(-0.5, 0.5)
            economic_variation = random.uniform(-0.1, 0.1)
            interest_variation = random.uniform(-1.0, 1.0)
            
            # Simulate some market trends
            current_hour = datetime.now().hour
            trend_factor = 1 + 0.02 * random.sin(current_hour / 24 * 2 * 3.14159)
            
            market_data = {
                'market_index': round((base_market_index + market_variation) * trend_factor, 2),
                'fuel_price': round(max(2.0, base_fuel_price + fuel_variation), 2),
                'economic_indicator': round(max(0.5, min(1.5, base_economic_indicator + economic_variation)), 3),
                'interest_rate': round(max(0.0, base_interest_rate + interest_variation), 2),
                'consumer_confidence': round(random.uniform(80, 120), 1),
                'inflation_rate': round(random.uniform(1.5, 4.0), 2),
                'unemployment_rate': round(random.uniform(3.0, 8.0), 1),
                'timestamp': datetime.now().isoformat(),
                'data_source': 'simulation'
            }
            
            # Add some seasonal effects
            month = datetime.now().month
            if month in [11, 12, 1]:  # Winter months
                market_data['seasonal_factor'] = 0.95  # Lower demand
            elif month in [5, 6, 7]:  # Summer months
                market_data['seasonal_factor'] = 1.05  # Higher demand
            else:
                market_data['seasonal_factor'] = 1.0
            
            logger.debug(f"Generated simulated market data: {market_data}")
            return market_data
            
        except Exception as e:
            logger.error(f"Error generating simulated market data: {e}")
            return self._get_default_market_data()
    
    def _get_real_market_data(self) -> Dict[str, Any]:
        """
        Fetch real market data from external APIs.
        
        This is a placeholder for real API integration.
        In production, this would make HTTP requests to market data providers.
        
        Returns:
            Dictionary containing real market data
        """
        try:
            # TODO: Implement real API calls
            # Example API integrations:
            # - Federal Reserve Economic Data (FRED)
            # - Alpha Vantage
            # - Yahoo Finance
            # - Bloomberg API
            
            logger.warning("Real market data API not implemented yet, using simulation")
            
            # For now, return simulated data with a note
            market_data = self._get_simulated_market_data()
            market_data['data_source'] = 'api_placeholder'
            
            return market_data
            
        except Exception as e:
            logger.error(f"Error fetching real market data: {e}")
            return self._get_simulated_market_data()
    
    def _get_default_market_data(self) -> Dict[str, Any]:
        """
        Get default market data as fallback.
        
        Returns:
            Dictionary containing default market values
        """
        return {
            'market_index': 1100.0,
            'fuel_price': 3.75,
            'economic_indicator': 0.95,
            'interest_rate': 5.5,
            'consumer_confidence': 100.0,
            'inflation_rate': 2.5,
            'unemployment_rate': 5.0,
            'seasonal_factor': 1.0,
            'timestamp': datetime.now().isoformat(),
            'data_source': 'default'
        }
    
    def _is_cache_valid(self) -> bool:
        """
        Check if cached data is still valid.
        
        Returns:
            True if cache is valid, False otherwise
        """
        if not self.last_update or not self.cached_data:
            return False
        
        time_since_update = (datetime.now() - self.last_update).total_seconds()
        return time_since_update < self.cache_ttl
    
    def get_market_trends(self, days: int = 7) -> Dict[str, Any]:
        """
        Get historical market trends for the specified number of days.
        
        Args:
            days: Number of days of historical data to return
            
        Returns:
            Dictionary containing historical market trends
        """
        try:
            trends = {
                'period_days': days,
                'start_date': (datetime.now() - timedelta(days=days)).isoformat(),
                'end_date': datetime.now().isoformat(),
                'trends': []
            }
            
            # Generate simulated historical data
            for i in range(days):
                date = datetime.now() - timedelta(days=days-i-1)
                
                # Create trend data with some correlation to simulate real patterns
                base_index = 1100 + i * 2 + random.uniform(-20, 20)
                
                trend_data = {
                    'date': date.date().isoformat(),
                    'market_index': round(base_index, 2),
                    'fuel_price': round(3.5 + i * 0.02 + random.uniform(-0.2, 0.2), 2),
                    'economic_indicator': round(0.95 + random.uniform(-0.05, 0.05), 3)
                }
                
                trends['trends'].append(trend_data)
            
            logger.info(f"Generated {days} days of market trends")
            return trends
            
        except Exception as e:
            logger.error(f"Error generating market trends: {e}")
            return {'error': str(e)}
    
    def get_market_summary(self) -> Dict[str, Any]:
        """
        Get a summary of current market conditions.
        
        Returns:
            Dictionary containing market condition summary
        """
        try:
            current_data = self.get_market_data()
            
            # Analyze market conditions
            market_index = current_data.get('market_index', 1100)
            fuel_price = current_data.get('fuel_price', 3.75)
            economic_indicator = current_data.get('economic_indicator', 0.95)
            
            # Determine market condition
            if market_index > 1150 and economic_indicator > 1.0:
                condition = 'bullish'
            elif market_index < 1050 and economic_indicator < 0.9:
                condition = 'bearish'
            else:
                condition = 'neutral'
            
            # Fuel price impact
            if fuel_price > 4.0:
                fuel_impact = 'negative'
            elif fuel_price < 3.5:
                fuel_impact = 'positive'
            else:
                fuel_impact = 'neutral'
            
            summary = {
                'overall_condition': condition,
                'market_index_level': 'high' if market_index > 1150 else 'low' if market_index < 1050 else 'normal',
                'fuel_price_impact': fuel_impact,
                'economic_strength': 'strong' if economic_indicator > 1.0 else 'weak' if economic_indicator < 0.9 else 'stable',
                'recommendation': self._get_market_recommendation(condition, fuel_impact),
                'last_updated': current_data.get('timestamp'),
                'data_freshness': 'cached' if self._is_cache_valid() else 'fresh'
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating market summary: {e}")
            return {'error': str(e)}
    
    def _get_market_recommendation(self, condition: str, fuel_impact: str) -> str:
        """
        Generate market recommendation based on conditions.
        
        Args:
            condition: Overall market condition
            fuel_impact: Fuel price impact assessment
            
        Returns:
            Market recommendation string
        """
        if condition == 'bullish' and fuel_impact != 'negative':
            return 'Favorable market conditions for vehicle sales'
        elif condition == 'bearish' or fuel_impact == 'negative':
            return 'Challenging market conditions, expect lower prices'
        else:
            return 'Stable market conditions, prices should remain steady'
    
    def refresh_cache(self) -> bool:
        """
        Force refresh of cached market data.
        
        Returns:
            True if refresh successful, False otherwise
        """
        try:
            self.get_market_data(force_refresh=True)
            return True
        except Exception as e:
            logger.error(f"Cache refresh failed: {e}")
            return False
