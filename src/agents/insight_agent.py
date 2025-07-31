import logging

logger = logging.getLogger(__name__)

class InsightAgent:
    def __init__(self, use_ollama=True):
        """
        Initialize Insight Agent with optional Ollama enhancement.
        
        Args:
            use_ollama: Whether to use Ollama for enhanced insights
        """
        self.use_ollama = use_ollama
        self.ollama_agent = None
        
        if use_ollama:
            try:
                from .ollama_agent import OllamaAgent
                self.ollama_agent = OllamaAgent()
                if self.ollama_agent.is_available():
                    logger.info("Ollama agent initialized for enhanced insights")
                else:
                    self.use_ollama = False
                    logger.info("Ollama not available, using standard insights")
            except Exception as e:
                logger.warning(f"Ollama initialization failed: {e}")
                self.use_ollama = False
    
    def recommend_action(self, predicted_price: float, explanation: str) -> str:
        """
        Generate actionable recommendations based on price and explanation.
        
        Args:
            predicted_price: The predicted vehicle price
            explanation: Explanation of the prediction
            
        Returns:
            str: Actionable recommendations
        """
        # Try Ollama for enhanced insights first
        if self.use_ollama and self.ollama_agent and self.ollama_agent.is_available():
            try:
                ollama_insights = self.ollama_agent.generate_insights(predicted_price, explanation)
                if ollama_insights and ollama_insights.strip():
                    logger.info("Generated insights using Ollama")
                    return f"🤖 AI-Enhanced Insights:\n\n{ollama_insights}"
            except Exception as e:
                logger.warning(f"Ollama insights failed, falling back to standard: {e}")
        
        # Fallback to standard rule-based insights
        return self._standard_insights(predicted_price, explanation)
    
    def _standard_insights(self, predicted_price: float, explanation: str) -> str:
        """
        Generate standard rule-based insights.
        
        Args:
            predicted_price: The predicted vehicle price
            explanation: Explanation of the prediction
            
        Returns:
            str: Standard insights and recommendations
        """
        insights = []
        
        # Price-based recommendations
        if predicted_price >= 40000:
            insights.append("💎 Premium vehicle - highlight luxury features and maintenance history")
            insights.append("📋 Professional inspection and detailed documentation recommended")
            insights.append("🕒 Market timing important for high-value vehicles")
        elif predicted_price >= 20000:
            insights.append("✅ Good market position - emphasize value proposition")
            insights.append("🔍 Compare with similar vehicles in your area")
            insights.append("📸 High-quality photos will maximize appeal")
        elif predicted_price >= 10000:
            insights.append("💰 Competitive pricing - focus on reliability and maintenance")
            insights.append("🔧 Address any minor issues before listing")
            insights.append("📍 Local market conditions matter at this price point")
        else:
            insights.append("🚗 Budget-friendly option - emphasize basic reliability")
            insights.append("💡 Consider quick sale strategies")
            insights.append("🔍 Highlight any recent maintenance or improvements")
        
        # Context-based recommendations from explanation
        explanation_lower = explanation.lower()
        if "high mileage" in explanation_lower or "mileage" in explanation_lower:
            insights.append("📊 High mileage noted - highlight service records")
        
        if "age" in explanation_lower or "older" in explanation_lower:
            insights.append("� Vehicle age factor - emphasize maintained condition")
        
        if "market" in explanation_lower:
            insights.append("�📈 Market conditions considered - monitor trends")
        
        # General recommendations
        insights.extend([
            "🔄 Regular market comparison recommended",
            "📝 Keep detailed records for future reference",
            "⚡ Act promptly in volatile market conditions"
        ])
        
        return "\n".join(insights[:5])  # Limit to top 5 insights
    
    def get_market_timing_advice(self, predicted_price: float) -> str:
        """
        Get specific advice about market timing.
        
        Args:
            predicted_price: The predicted vehicle price
            
        Returns:
            str: Market timing advice
        """
        if predicted_price >= 30000:
            return "🕒 Premium vehicles: Spring/summer typically better for selling"
        elif predicted_price >= 15000:
            return "� Mid-range vehicles: Consistent demand, timing less critical"
        else:
            return "⚡ Budget vehicles: Quick turnover often better than waiting"
    
    def get_negotiation_tips(self, predicted_price: float) -> str:
        """
        Get negotiation tips based on predicted price.
        
        Args:
            predicted_price: The predicted vehicle price
            
        Returns:
            str: Negotiation tips
        """
        tips = []
        
        if predicted_price >= 25000:
            tips.extend([
                "💼 Professional approach - detailed documentation helps",
                "🔍 Be prepared for thorough inspections",
                "💰 Leave room for negotiation (5-10%)"
            ])
        else:
            tips.extend([
                "🤝 Flexible approach often works better",
                "⚡ Quick decisions can be advantageous",
                "💡 Small improvements can justify asking price"
            ])
        
        return "\n".join(tips)