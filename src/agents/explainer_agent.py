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
    def __init__(self, use_mock=True, use_ollama=True):
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
        
        # Initialize Ollama agent if requested
        self.use_ollama = use_ollama
        self.ollama_agent = None
        if use_ollama:
            try:
                from .ollama_agent import OllamaAgent
                self.ollama_agent = OllamaAgent()
                if self.ollama_agent.is_available():
                    logger.info("Ollama agent initialized for enhanced explanations")
                else:
                    self.use_ollama = False
                    logger.info("Ollama not available, using standard explanations")
            except Exception as e:
                logger.warning(f"Ollama initialization failed: {e}")
                self.use_ollama = False

    def explain(self, input_data, predicted_price):
        # Try Ollama first for enhanced explanations
        if self.use_ollama and self.ollama_agent and self.ollama_agent.is_available():
            try:
                vehicle_data = {
                    'vehicle_age': input_data.get('vehicle_age'),
                    'mileage': input_data.get('mileage'),
                    'brand': input_data.get('brand', 'Unknown'),
                    'model': input_data.get('model', 'Unknown')
                }
                market_data = {
                    'market_index': input_data.get('market_index'),
                    'fuel_price': input_data.get('fuel_price')
                }
                
                ollama_explanation = self.ollama_agent.generate_explanation(
                    vehicle_data, market_data, predicted_price
                )
                
                if ollama_explanation and ollama_explanation.strip():
                    logger.info("Generated explanation using Ollama")
                    return f"🤖 AI-Enhanced Analysis:\n\n{ollama_explanation}"
                
            except Exception as e:
                logger.warning(f"Ollama explanation failed, falling back to standard: {e}")
        
        # Fallback to standard RAG-based explanation
        return self._standard_explanation(input_data, predicted_price)
    
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
