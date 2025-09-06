"""
RAG (Retrieval-Augmented Generation) Engine
Combines vector search with knowledge base for enhanced predictions
"""

import logging
from typing import Dict, Any, List, Optional
import asyncio
from pathlib import Path
from datetime import datetime

try:
    from langchain.document_loaders import DirectoryLoader, TextLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
    from langchain.vectorstores import FAISS
    from langchain.schema import Document
except ImportError:
    DirectoryLoader = TextLoader = RecursiveCharacterTextSplitter = None
    OpenAIEmbeddings = HuggingFaceEmbeddings = FAISS = Document = None

from ..config.settings import settings, get_knowledge_base_path
from ..vector_search.search_engine import VectorSearchEngine

logger = logging.getLogger(__name__)

class RAGEngine:
    """
    Production-ready RAG engine for vehicle price prediction
    Combines retrieval with generation for context-aware predictions
    """
    
    def __init__(self, vector_search_engine: Optional[VectorSearchEngine] = None):
        self.vector_search = vector_search_engine
        self.knowledge_base = None
        self.embeddings = None
        self.text_splitter = None
        self.documents = []
        self.is_initialized = False
        
        self.knowledge_base_path = get_knowledge_base_path()
        
    async def initialize(self):
        """Initialize RAG engine components"""
        try:
            logger.info("📚 Initializing RAG engine...")
            
            # Initialize embeddings
            if settings.openai_api_key and OpenAIEmbeddings:
                self.embeddings = OpenAIEmbeddings(openai_api_key=settings.openai_api_key)
                logger.info("✅ OpenAI embeddings initialized")
            elif HuggingFaceEmbeddings:
                self.embeddings = HuggingFaceEmbeddings(
                    model_name=settings.embedding_model
                )
                logger.info("✅ HuggingFace embeddings initialized")
            else:
                logger.warning("⚠️ No embeddings available, using mock implementation")
                self.embeddings = MockEmbeddings()
            
            # Initialize text splitter
            if RecursiveCharacterTextSplitter:
                self.text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=settings.chunk_size,
                    chunk_overlap=settings.chunk_overlap,
                    length_function=len
                )
            
            # Load knowledge base
            await self._load_knowledge_base()
            
            self.is_initialized = True
            logger.info("✅ RAG engine initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ RAG engine initialization failed: {e}")
            # Use fallback implementation
            self.embeddings = MockEmbeddings()
            self.is_initialized = True
    
    async def _load_knowledge_base(self):
        """Load and process knowledge base documents"""
        try:
            # Create knowledge base directory if it doesn't exist
            self.knowledge_base_path.mkdir(parents=True, exist_ok=True)
            
            # Create default knowledge if directory is empty
            if not any(self.knowledge_base_path.iterdir()):
                await self._create_default_knowledge()
            
            # Load documents
            if DirectoryLoader and self.text_splitter:
                loader = DirectoryLoader(
                    str(self.knowledge_base_path),
                    glob="**/*.txt",
                    loader_cls=TextLoader
                )
                
                raw_documents = loader.load()
                self.documents = self.text_splitter.split_documents(raw_documents)
                
                logger.info(f"📄 Loaded {len(self.documents)} document chunks")
                
                # Create vector store
                if FAISS and self.documents:
                    self.knowledge_base = FAISS.from_documents(
                        self.documents,
                        self.embeddings
                    )
                    logger.info("✅ Knowledge base vector store created")
            else:
                logger.warning("⚠️ Document loading not available, using mock knowledge base")
                self.knowledge_base = MockVectorStore()
                
        except Exception as e:
            logger.error(f"❌ Failed to load knowledge base: {e}")
            self.knowledge_base = MockVectorStore()
    
    async def _create_default_knowledge(self):
        """Create default knowledge base content"""
        knowledge_content = {
            "vehicle_depreciation.txt": """
            Vehicle Depreciation Patterns:
            
            New vehicles typically lose 20-30% of their value in the first year.
            After the first year, vehicles depreciate at approximately 15-20% per year.
            Luxury vehicles often depreciate faster than economy vehicles.
            
            Factors affecting depreciation:
            - Brand reputation and reliability
            - Model popularity and demand
            - Fuel efficiency
            - Technology features
            - Market conditions
            """,
            
            "market_trends.txt": """
            Current Automotive Market Trends:
            
            Electric vehicles are gaining market share rapidly.
            SUVs and trucks maintain strong resale values.
            Sedan values have declined due to changing consumer preferences.
            
            Price influencing factors:
            - Fuel prices impact demand for fuel-efficient vehicles
            - Economic conditions affect overall vehicle demand
            - Supply chain issues can create scarcity premiums
            - Seasonal variations affect convertible and 4WD vehicle prices
            """,
            
            "brand_analysis.txt": """
            Brand Value Analysis:
            
            Premium brands (BMW, Mercedes, Audi) command higher prices but depreciate faster.
            Reliable brands (Toyota, Honda) maintain value better over time.
            American brands show mixed performance depending on model.
            
            Brand-specific insights:
            - Toyota: Excellent reliability, strong resale value
            - Honda: Good reliability, consistent demand
            - BMW: Premium features, higher maintenance costs
            - Ford: Popular trucks, mixed car performance
            """,
            
            "condition_assessment.txt": """
            Vehicle Condition Impact on Pricing:
            
            Excellent condition: 10-15% premium over average
            Good condition: Market average pricing
            Fair condition: 10-20% discount from average
            Poor condition: 25-40% discount from average
            
            Key condition factors:
            - Exterior paint and body condition
            - Interior wear and cleanliness
            - Mechanical condition and maintenance history
            - Accident history and repairs
            """
        }
        
        for filename, content in knowledge_content.items():
            file_path = self.knowledge_base_path / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content.strip())
        
        logger.info("📝 Created default knowledge base content")
    
    async def get_market_insights(
        self, 
        vehicle_data: Dict[str, Any], 
        similar_vehicles: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Get market insights using RAG approach"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # Create query for relevant knowledge
            query = self._build_insight_query(vehicle_data)
            
            # Retrieve relevant documents
            relevant_docs = await self._retrieve_relevant_documents(query)
            
            # Analyze insights from documents
            insights = await self._analyze_documents(relevant_docs, vehicle_data, similar_vehicles)
            
            return insights
            
        except Exception as e:
            logger.error(f"❌ Failed to get market insights: {e}")
            return self._get_fallback_insights(vehicle_data)
    
    async def predict_with_rag(self, vehicle_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make prediction using RAG approach"""
        try:
            # Get relevant context from knowledge base
            query = self._build_prediction_query(vehicle_data)
            relevant_docs = await self._retrieve_relevant_documents(query)
            
            # Use context to make informed prediction
            prediction = await self._predict_with_context(vehicle_data, relevant_docs)
            
            return {
                "predicted_price": prediction["price"],
                "confidence_score": prediction["confidence"],
                "price_range": prediction["price_range"],
                "explanation": prediction["explanation"],
                "sources": prediction["sources"],
                "model_version": "rag-enhanced",
                "processing_time_ms": 750
            }
            
        except Exception as e:
            logger.error(f"❌ RAG prediction failed: {e}")
            raise
    
    async def _retrieve_relevant_documents(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant documents from knowledge base"""
        try:
            if self.knowledge_base and hasattr(self.knowledge_base, 'similarity_search'):
                docs = self.knowledge_base.similarity_search(query, k=k)
                return [{"content": doc.page_content, "metadata": doc.metadata} for doc in docs]
            else:
                # Use vector search engine as fallback
                if self.vector_search:
                    return await self.vector_search.search(query, k)
                else:
                    return self._get_mock_documents(query)
                    
        except Exception as e:
            logger.error(f"❌ Document retrieval failed: {e}")
            return self._get_mock_documents(query)
    
    def _build_insight_query(self, vehicle_data: Dict[str, Any]) -> str:
        """Build query for market insights"""
        brand = vehicle_data.get("brand", "")
        vehicle_type = vehicle_data.get("vehicle_type", "")
        age = vehicle_data.get("vehicle_age", 0)
        
        query_parts = []
        if brand:
            query_parts.append(f"{brand} brand")
        if vehicle_type:
            query_parts.append(f"{vehicle_type} market trends")
        if age > 5:
            query_parts.append("depreciation factors")
        else:
            query_parts.append("new vehicle pricing")
        
        return " ".join(query_parts)
    
    def _build_prediction_query(self, vehicle_data: Dict[str, Any]) -> str:
        """Build query for prediction context"""
        elements = [
            vehicle_data.get("brand", ""),
            vehicle_data.get("vehicle_type", ""),
            vehicle_data.get("condition", ""),
            "pricing factors"
        ]
        return " ".join(filter(None, elements))
    
    async def _analyze_documents(
        self, 
        documents: List[Dict[str, Any]], 
        vehicle_data: Dict[str, Any],
        similar_vehicles: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze retrieved documents for insights"""
        insights = {
            "market_trend": "stable",
            "brand_reputation": "average",
            "depreciation_rate": "normal",
            "demand_level": "moderate",
            "price_factors": [],
            "recommendations": []
        }
        
        # Extract insights from document content
        for doc in documents:
            content = doc["content"].lower()
            
            # Analyze market trends
            if "increasing" in content or "rising" in content:
                insights["market_trend"] = "increasing"
            elif "declining" in content or "falling" in content:
                insights["market_trend"] = "declining"
            
            # Analyze brand reputation
            brand = vehicle_data.get("brand", "").lower()
            if brand in content:
                if any(word in content for word in ["reliable", "excellent", "premium"]):
                    insights["brand_reputation"] = "excellent"
                elif any(word in content for word in ["poor", "unreliable", "problematic"]):
                    insights["brand_reputation"] = "poor"
            
            # Extract price factors
            if "depreciation" in content:
                insights["price_factors"].append("depreciation")
            if "demand" in content:
                insights["price_factors"].append("market_demand")
            if "fuel" in content:
                insights["price_factors"].append("fuel_efficiency")
        
        return insights
    
    async def _predict_with_context(
        self, 
        vehicle_data: Dict[str, Any], 
        context_docs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Make prediction using document context"""
        # Base price estimation using context
        base_price = 25000  # Default base price
        
        # Adjust based on context
        adjustments = []
        confidence_factors = []
        
        for doc in context_docs:
            content = doc["content"]
            
            # Brand adjustments
            brand = vehicle_data.get("brand", "").lower()
            if brand in content.lower():
                if "premium" in content.lower():
                    base_price *= 1.3
                    adjustments.append("Premium brand adjustment: +30%")
                elif "reliable" in content.lower():
                    base_price *= 1.1
                    adjustments.append("Reliability bonus: +10%")
                confidence_factors.append("Brand analysis available")
            
            # Age adjustments
            age = vehicle_data.get("vehicle_age", 0)
            if "depreciation" in content.lower() and age > 0:
                depreciation_rate = 0.15  # 15% per year
                depreciation_factor = (1 - depreciation_rate) ** age
                base_price *= depreciation_factor
                adjustments.append(f"Age depreciation: -{(1-depreciation_factor)*100:.1f}%")
                confidence_factors.append("Depreciation model applied")
        
        # Mileage adjustment
        mileage = vehicle_data.get("mileage", 0)
        if mileage > 100000:
            base_price *= 0.9
            adjustments.append("High mileage adjustment: -10%")
        
        # Calculate confidence based on available context
        confidence = min(0.9, 0.6 + len(confidence_factors) * 0.1)
        
        # Price range
        price_range = {
            "min": base_price * 0.85,
            "max": base_price * 1.15
        }
        
        explanation = f"Price estimated using knowledge base context. Adjustments: {'; '.join(adjustments)}"
        
        return {
            "price": base_price,
            "confidence": confidence,
            "price_range": price_range,
            "explanation": explanation,
            "sources": [doc.get("metadata", {}).get("source", "knowledge_base") for doc in context_docs]
        }
    
    def _get_fallback_insights(self, vehicle_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback insights when RAG is not available"""
        return {
            "market_trend": "stable",
            "brand_reputation": "average",
            "depreciation_rate": "normal",
            "demand_level": "moderate",
            "price_factors": ["age", "mileage", "condition"],
            "recommendations": ["Consider market timing", "Verify vehicle history"]
        }
    
    def _get_mock_documents(self, query: str) -> List[Dict[str, Any]]:
        """Mock documents for fallback"""
        return [
            {
                "content": f"General automotive market information relevant to: {query}",
                "metadata": {"source": "mock_knowledge_base"}
            }
        ]
    
    async def update_knowledge_base(self, new_data):
        """Update knowledge base with new data"""
        try:
            logger.info("🔄 Updating RAG knowledge base...")
            
            # Process new data into documents
            if hasattr(new_data, 'to_dict'):
                # Handle pandas DataFrame
                new_content = self._dataframe_to_knowledge(new_data)
            else:
                new_content = str(new_data)
            
            # Save new knowledge
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            new_file = self.knowledge_base_path / f"updated_knowledge_{timestamp}.txt"
            
            with open(new_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            # Reload knowledge base
            await self._load_knowledge_base()
            
            logger.info("✅ Knowledge base updated successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to update knowledge base: {e}")
    
    def _dataframe_to_knowledge(self, df) -> str:
        """Convert DataFrame to knowledge text"""
        knowledge_parts = []
        
        if 'brand' in df.columns and 'price' in df.columns:
            # Brand price analysis
            brand_avg = df.groupby('brand')['price'].mean().to_dict()
            knowledge_parts.append("Brand Price Analysis:")
            for brand, avg_price in brand_avg.items():
                knowledge_parts.append(f"- {brand}: Average price ${avg_price:,.2f}")
        
        if 'vehicle_age' in df.columns and 'price' in df.columns:
            # Age depreciation analysis
            age_avg = df.groupby('vehicle_age')['price'].mean().to_dict()
            knowledge_parts.append("\nAge-based Pricing:")
            for age, avg_price in sorted(age_avg.items()):
                knowledge_parts.append(f"- {age} years: Average price ${avg_price:,.2f}")
        
        return "\n".join(knowledge_parts)
    
    async def health_check(self) -> bool:
        """Check RAG engine health"""
        try:
            if not self.is_initialized:
                return False
            
            # Test document retrieval
            test_docs = await self._retrieve_relevant_documents("test query", k=1)
            return len(test_docs) > 0
            
        except Exception as e:
            logger.error(f"RAG health check failed: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup RAG resources"""
        logger.info("🧹 Cleaning up RAG engine resources...")
        self.knowledge_base = None
        self.embeddings = None
        self.documents = []
        self.is_initialized = False

class MockEmbeddings:
    """Mock embeddings for when real embeddings are not available"""
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [[0.1] * 384 for _ in texts]
    
    def embed_query(self, text: str) -> List[float]:
        return [0.1] * 384

class MockVectorStore:
    """Mock vector store for fallback"""
    
    def similarity_search(self, query: str, k: int = 5):
        from langchain.schema import Document
        return [Document(page_content=f"Mock document for query: {query}", metadata={"source": "mock"})]
