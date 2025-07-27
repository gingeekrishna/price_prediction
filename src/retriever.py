import random

class RetrieverAgent:
    def get_market_data(self):
        # Simulated real-time market data
        return {
            "market_index": round(random.uniform(950, 1150), 2),
            "fuel_price": round(random.uniform(3.0, 4.0), 2)
        }
