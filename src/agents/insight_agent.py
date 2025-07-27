class InsightAgent:
    def recommend_action(self, predicted_price: float, explanation: str) -> str:
        if predicted_price >= 20000:
            return "✅ List as premium vehicle. Emphasize its high value."
        elif "demand" in explanation.lower():
            return "📈 Market demand is high — consider listing soon."
        elif predicted_price < 10000:
            return "💡 Consider price adjustment or marketing boost."
        return "👍 Use standard pricing and monitor performance."