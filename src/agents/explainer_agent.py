# import openai
# from openai import OpenAIError

# class ExplainerAgent:
#     def __init__(self, model="gpt-3.5-turbo"):
#         self.model = model

#     def explain(self, input_data: dict, price: float):
#         prompt = f"Explain why a vehicle with the following data:\n{input_data}\nwas priced at ${price:.2f}."
#         try:
#             response = openai.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[{"role": "user", "content": prompt}],
#             temperature=0.7
#         )
#             return response.choices[0].message.content.strip()
#         except OpenAIError as e:
#             # Fallback explanation if API call fails
#             print(f"OpenAI API error: {e}. Returning fallback explanation.")
#             return (
#                 f"Based on the vehicle features {input_data} and market conditions, "
#                 f"a predicted price of ${price:.2f} is reasonable."
#             )
    
from src.mock import DummyEmbeddings, DummyChatCompletion
from langchain.vectorstores import FAISS
import logging

logger = logging.getLogger(__name__)

class ExplainerAgentRAG:
    def __init__(self, use_mock=True, use_ollama=True, use_claude=False, llm_provider="ollama"):
        """
        Initialize ExplainerAgentRAG with multiple LLM options.
        
        Args:
            use_mock: Use mock embeddings and chat completion
            use_ollama: Enable Ollama LLM support
            use_claude: Enable Claude LLM support  
            llm_provider: Primary LLM provider ("ollama", "claude", or "auto")
        """
        if use_mock:
            self.embeddings = DummyEmbeddings()
            self.chat_completion = DummyChatCompletion()
            self.vectorstore = None
        else:
            from langchain.embeddings import OpenAIEmbeddings
            import openai
            self.embeddings = OpenAIEmbeddings()
            self.chat_completion = openai.chat.completions
            try:
                self.vectorstore = FAISS.load_local("faiss_index", self.embeddings)
                print(f"Loaded FAISS index with {self.vectorstore.index.ntotal} vectors.")
            except Exception as e:
                logger.warning(f"Failed to load FAISS index: {e}")
                self.vectorstore = None
        
        # Initialize LLM providers
        self.llm_provider = llm_provider
        self.use_ollama = use_ollama
        self.use_claude = use_claude
        self.ollama_agent = None
        self.claude_agent = None
        
        # Initialize Ollama agent if requested
        if use_ollama:
            try:
                from .ollama_agent import OllamaAgent
                self.ollama_agent = OllamaAgent()
                if self.ollama_agent.available:
                    logger.info("Ollama agent initialized for enhanced explanations")
                else:
                    self.use_ollama = False
                    logger.info("Ollama not available")
            except Exception as e:
                logger.warning(f"Ollama initialization failed: {e}")
                self.use_ollama = False
        
        # Initialize Claude agent if requested
        if use_claude:
            try:
                from .claude_agent import ClaudeAgent
                self.claude_agent = ClaudeAgent()
                if self.claude_agent.available:
                    logger.info("Claude agent initialized for enhanced explanations")
                else:
                    self.use_claude = False
                    logger.info("Claude not available - check ANTHROPIC_API_KEY")
            except Exception as e:
                logger.warning(f"Claude initialization failed: {e}")
                self.use_claude = False

    def explain(self, input_data, predicted_price):
        """Generate explanation using the best available LLM provider."""
        
        # Prepare standardized vehicle and market data
        vehicle_data = {
            'vehicle_age': input_data.get('vehicle_age'),
            'mileage': input_data.get('mileage'),
            'make': input_data.get('make', input_data.get('brand', 'Unknown')),
            'model': input_data.get('model', 'Unknown'),
            'year': input_data.get('year')
        }
        market_data = {
            'market_index': input_data.get('market_index'),
            'fuel_price': input_data.get('fuel_price'),
            'avg_price': predicted_price,
            'trend': 'stable'
        }
        
        # Try providers based on preference and availability
        if self.llm_provider == "claude" and self.use_claude and self.claude_agent:
            explanation = self._try_claude_explanation(vehicle_data, market_data, predicted_price)
            if explanation:
                return f"🧠 Claude AI Analysis:\n\n{explanation}"
                
        elif self.llm_provider == "ollama" and self.use_ollama and self.ollama_agent:
            explanation = self._try_ollama_explanation(vehicle_data, market_data, predicted_price)
            if explanation:
                return f"🤖 Ollama AI Analysis:\n\n{explanation}"
                
        elif self.llm_provider == "auto":
            # Try Claude first (faster), then Ollama, then fallback
            if self.use_claude and self.claude_agent:
                explanation = self._try_claude_explanation(vehicle_data, market_data, predicted_price)
                if explanation:
                    return f"🧠 Claude AI Analysis:\n\n{explanation}"
                    
            if self.use_ollama and self.ollama_agent:
                explanation = self._try_ollama_explanation(vehicle_data, market_data, predicted_price)
                if explanation:
                    return f"🤖 Ollama AI Analysis:\n\n{explanation}"
        
        # Fallback to standard RAG-based explanation
        return self._standard_explanation(input_data, predicted_price)
    
    def _try_claude_explanation(self, vehicle_data, market_data, predicted_price):
        """Try to generate explanation using Claude."""
        try:
            if self.claude_agent and self.claude_agent.available:
                explanation = self.claude_agent.generate_explanation(
                    vehicle_data, market_data, predicted_price
                )
                if explanation and explanation.strip() and "error" not in explanation.lower():
                    logger.info("Generated explanation using Claude")
                    return explanation
        except Exception as e:
            logger.warning(f"Claude explanation failed: {e}")
        return None
    
    def _try_ollama_explanation(self, vehicle_data, market_data, predicted_price):
        """Try to generate explanation using Ollama."""
        try:
            if self.ollama_agent and self.ollama_agent.available:
                explanation = self.ollama_agent.generate_explanation(
                    vehicle_data, market_data, predicted_price
                )
                if explanation and explanation.strip():
                    logger.info("Generated explanation using Ollama")
                    return explanation
        except Exception as e:
            logger.warning(f"Ollama explanation failed: {e}")
        return None
    
    def _standard_explanation(self, input_data, predicted_price):
        """Standard explanation using RAG or fallback methods."""
        # Convert input_data to a query string or text for retrieval
        query_text = str(input_data)

        # Use vectorstore to retrieve relevant docs if available
        relevant_docs = []
        if self.vectorstore:
            try:
                relevant_docs = self.vectorstore.similarity_search(query_text, k=3)
                print("Retrieved documents for explanation:", relevant_docs)
            except Exception as e:
                logger.warning(f"Vectorstore query failed: {e}")

        # Build prompt including relevant docs context
        context_text = "\n".join([doc.page_content for doc in relevant_docs]) if relevant_docs else ""
        prompt = (
            f"Context: {context_text}\n\n"
            f"Explain why a vehicle with features {input_data} is priced at ${predicted_price:.2f}."
        )
        
        try:
            if hasattr(self, 'chat_completion') and isinstance(self.chat_completion, DummyChatCompletion):
                response = self.chat_completion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}])
            else:
                response = self.chat_completion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Standard explanation failed: {e}")
            return self._fallback_explanation(input_data, predicted_price)
    
    def _fallback_explanation(self, input_data, predicted_price):
        """Simple fallback explanation when all other methods fail."""
        vehicle_age = input_data.get('vehicle_age', 'Unknown')
        mileage = input_data.get('mileage', 'Unknown')
        
        return f"""📊 Price Analysis: ${predicted_price:,.2f}

Key Factors:
• Vehicle Age: {vehicle_age} years - Age affects depreciation
• Mileage: {mileage} km - Higher mileage typically reduces value
• Market Conditions: Current economic factors considered
• Model Features: Standard features and condition assumed

This prediction is based on market trends and depreciation patterns typical for similar vehicles."""
