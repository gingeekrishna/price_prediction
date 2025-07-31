# src/agents/market_data_agent.py
import random
import time

class MarketDataAgent:
    def fetch(self):
        # Add some realistic variation to market data
        # Base values with small random variations
        base_market_index = 1120.5
        base_fuel_price = 3.75
        
        # Add random variation (+/- 5% for market index, +/- 10% for fuel price)
        market_variation = random.uniform(-0.05, 0.05)
        fuel_variation = random.uniform(-0.10, 0.10)
        
        market_index = round(base_market_index * (1 + market_variation), 2)
        fuel_price = round(base_fuel_price * (1 + fuel_variation), 2)
        
        return {
            "market_index": market_index,
            "fuel_price": fuel_price
        }
