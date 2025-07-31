# Agentic RAG (Retrieval-Augmented Generation) Pattern Integration

This document describes the Agentic RAG pattern implementation for intelligent knowledge retrieval and generation in the Vehicle Price Prediction system.

## Overview

The Agentic RAG pattern combines Retrieval-Augmented Generation (RAG) with intelligent agents to create a sophisticated knowledge management and query system. It enables the system to store, retrieve, and reason over historical data, explanations, and domain knowledge to provide enhanced insights and predictions.

## Architecture Components

### Core RAG Components

#### 1. KnowledgeStore
- **Purpose**: Database-backed storage with vector search capabilities
- **Features**:
  - SQLite database for persistent storage
  - FAISS vector indexing for similarity search
  - Full-text search using SQLite FTS5
  - Hybrid search combining vector and text search
  - Automatic embedding generation

#### 2. KnowledgeChunk
- **Structure**: Represents a piece of knowledge with metadata
- **Properties**:
  - Unique ID and content
  - Vector embeddings for similarity search
  - Rich metadata and tagging
  - Source tracking and timestamps
  - Relevance scoring

#### 3. AgenticRagCoordinator
- **Purpose**: Orchestrates multiple specialized RAG agents
- **Capabilities**:
  - Intelligent query routing
  - Multi-agent coordination
  - Query history tracking
  - Performance monitoring

### Specialized RAG Agents

#### 1. VehiclePriceRagAgent
- **Specialization**: Vehicle pricing analysis and predictions
- **Capabilities**:
  - Price prediction analysis
  - Feature importance explanation
  - Historical data retrieval
  - Comparative analysis

#### 2. MarketTrendRagAgent
- **Specialization**: Market trend analysis and economic indicators
- **Capabilities**:
  - Market trend analysis
  - Seasonal pattern analysis
  - Economic indicator analysis
  - Demand-supply analysis

### Integration Components

#### 1. KnowledgeIngestionPipeline
- **Purpose**: Automated knowledge ingestion from multiple sources
- **Supported Sources**:
  - Text documents and files
  - Structured vehicle data
  - Market data and trends
  - Prediction results and explanations

#### 2. BlackboardRagAgent
- **Purpose**: Integration with blackboard coordination pattern
- **Capabilities**:
  - Automatic knowledge ingestion from blackboard messages
  - RAG query handling within workflows
  - Knowledge sharing across agents

## Database Schema

### Knowledge Store Tables

```sql
-- Main knowledge chunks table
CREATE TABLE knowledge_chunks (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    metadata TEXT,           -- JSON metadata
    embedding BLOB,          -- Vector embedding
    created_at TEXT,
    updated_at TEXT,
    source TEXT,
    chunk_type TEXT,
    relevance_score REAL DEFAULT 0.0
);

-- Full-text search table
CREATE VIRTUAL TABLE knowledge_fts USING fts5(
    id, content, metadata, source
);

-- Blackboard activity logging
CREATE TABLE blackboard_activity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id TEXT,
    message_type TEXT,
    sender TEXT,
    timestamp TEXT,
    priority TEXT,
    data_summary TEXT,
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## API Endpoints

### RAG Query Endpoints

#### `/rag/query`
Natural language queries using the RAG system:

```json
POST /rag/query
{
  "query": "How does vehicle age affect pricing?",
  "context": {
    "predicted_price": 22500.0,
    "vehicle_age": 3
  }
}
```

**Response:**
```json
{
  "query": "How does vehicle age affect pricing?",
  "response": "Vehicle age is a primary depreciation factor...",
  "confidence": 0.85,
  "sources": ["pricing_guide", "market_analysis"],
  "selected_agent": "vehicle_price_rag",
  "relevant_chunks": 5,
  "timestamp": "2025-07-31T10:30:00Z",
  "rag_enabled": true
}
```

#### `/rag/ingest`
Ingest new knowledge into the system:

```json
POST /rag/ingest
{
  "content": "Market analysis shows increased demand for electric vehicles...",
  "source": "market_report_2025",
  "chunk_strategy": "paragraph",
  "metadata": {
    "topic": "electric_vehicles",
    "tags": ["market", "trends", "ev"]
  }
}
```

#### `/rag/knowledge/stats`
Get knowledge store statistics:

```json
GET /rag/knowledge/stats
```

**Response:**
```json
{
  "knowledge_stats": {
    "total_chunks": 1250,
    "unique_sources": 45,
    "source_breakdown": {
      "prediction_results": 450,
      "explanations": 300,
      "market_data": 250,
      "external_documents": 250
    },
    "faiss_vectors": 1250,
    "embedding_model": "all-MiniLM-L6-v2",
    "embeddings_available": true,
    "faiss_available": true
  },
  "available": true,
  "timestamp": "2025-07-31T10:30:00Z"
}
```

#### `/rag/knowledge/search`
Search the knowledge store:

```
GET /rag/knowledge/search?query=vehicle%20depreciation&search_type=hybrid&limit=10
```

### Enhanced Prediction Endpoints

#### `/predict_rag_enhanced`
Complete prediction with RAG-powered analysis:

```json
POST /predict_rag_enhanced
{
  "vehicle_age": 3,
  "mileage": 45000,
  "include_rag_analysis": true
}
```

**Response:**
```json
{
  "request_id": "pred_1234567890",
  "predicted_price": 22500.0,
  "input_data": {...},
  "market_data": {...},
  "explanation": "Standard explanation...",
  "recommendation": "Standard recommendation...",
  "rag_analysis": {
    "response": "Based on historical data analysis, this vehicle...",
    "confidence": 0.78,
    "sources": ["historical_data", "pricing_models"],
    "selected_agent": "vehicle_price_rag"
  },
  "processing_time": 2.34,
  "workflow_complete": true,
  "rag_enhanced": true,
  "agents_used": ["market", "prediction", "explainer", "insight", "rag"],
  "workflow_pattern": "blackboard_with_rag"
}
```

## Usage Examples

### Basic RAG Query

```python
from src.agentic_rag import KnowledgeStore, AgenticRagCoordinator

# Initialize RAG system
knowledge_store = KnowledgeStore("vehicle_knowledge.db")
rag_coordinator = AgenticRagCoordinator(knowledge_store)

# Query the system
result = await rag_coordinator.process_query(
    "What factors most influence vehicle depreciation?",
    context={"vehicle_type": "sedan"}
)

print(f"Response: {result['response']}")
print(f"Confidence: {result['confidence']}")
print(f"Sources: {result['sources']}")
```

### Knowledge Ingestion

```python
from src.agentic_rag import KnowledgeIngestionPipeline

# Initialize ingestion pipeline
pipeline = KnowledgeIngestionPipeline(knowledge_store)

# Ingest vehicle data
vehicle_records = [
    {
        "id": "v001",
        "brand": "Toyota",
        "model": "Camry",
        "age": 3,
        "mileage": 45000,
        "price": 22500.0,
        "features": ["bluetooth", "backup_camera"]
    }
]

count = await pipeline.ingest_vehicle_data(vehicle_records, "dealership_data")
print(f"Ingested {count} vehicle records")
```

### Blackboard Integration

```python
from src.blackboard_agents import VehiclePriceWorkflowCoordinator

# Create workflow with RAG enabled
workflow = VehiclePriceWorkflowCoordinator(
    use_ollama=True, 
    enable_rag=True
)
workflow.start()

try:
    # Enhanced prediction with RAG
    result = await workflow.predict_price(
        vehicle_age=3,
        mileage=45000,
        include_rag_analysis=True
    )
    
    print(f"Price: ${result['predicted_price']:.2f}")
    print(f"RAG Analysis: {result['rag_analysis']['response']}")
    
finally:
    workflow.stop()
```

### Custom RAG Agent

```python
from src.agentic_rag import RagAgent

class CustomInsuranceRagAgent(RagAgent):
    """Custom RAG agent for insurance analysis."""
    
    def __init__(self, knowledge_store):
        super().__init__("insurance_rag", knowledge_store)
        self.capabilities = ["insurance_analysis", "risk_assessment"]
    
    async def process_query(self, query, context=None):
        # Custom processing logic
        chunks = self.knowledge_store.search_hybrid(query, top_k=5)
        
        # Filter for insurance-related content
        insurance_chunks = [
            c for c in chunks 
            if 'insurance' in c.metadata.get('tags', [])
        ]
        
        if not insurance_chunks:
            return {
                'query': query,
                'response': "No insurance-related information found.",
                'confidence': 0.0
            }
        
        # Generate response
        response = self._generate_insurance_analysis(insurance_chunks, context)
        
        return {
            'query': query,
            'response': response,
            'confidence': self._calculate_confidence(insurance_chunks),
            'relevant_chunks': len(insurance_chunks)
        }
    
    def get_capabilities(self):
        return self.capabilities.copy()
```

## Search Strategies

### Vector Search
- **Use Case**: Semantic similarity queries
- **Technology**: FAISS with sentence transformers
- **Advantages**: Finds conceptually related content
- **Example**: "vehicle depreciation" matches "car value loss"

### Text Search
- **Use Case**: Exact term matching
- **Technology**: SQLite FTS5
- **Advantages**: Fast, precise keyword matching
- **Example**: "Toyota Camry" finds exact model references

### Hybrid Search
- **Use Case**: Best of both approaches
- **Method**: Combines vector and text scores
- **Configuration**: Adjustable weighting (default 70% vector, 30% text)
- **Advantages**: Balanced precision and recall

## Chunking Strategies

### Fixed Size Chunking
```python
# Split content into fixed-size pieces with overlap
chunks = pipeline._chunk_fixed_size(content, chunk_size=500, overlap=50)
```

### Sentence-Based Chunking
```python
# Split by sentence boundaries
chunks = pipeline._chunk_by_sentence(content)
```

### Paragraph-Based Chunking
```python
# Split by paragraph breaks (default)
chunks = pipeline._chunk_by_paragraph(content)
```

### Semantic Chunking
```python
# Intelligent content-aware splitting (future enhancement)
chunks = pipeline._chunk_semantic(content)
```

## Performance Optimization

### Embedding Model Selection

| Model | Size | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| `all-MiniLM-L6-v2` | 80MB | Fast | Good | General purpose (default) |
| `all-mpnet-base-v2` | 420MB | Medium | Excellent | High accuracy |
| `distilbert-base-nli-stsb-mean-tokens` | 250MB | Fast | Good | Lightweight |

### FAISS Index Types

```python
# Inner Product (cosine similarity)
index = faiss.IndexFlatIP(dimension)  # Default

# L2 Distance (Euclidean)
index = faiss.IndexFlatL2(dimension)

# Approximate search for large datasets
index = faiss.IndexIVFFlat(quantizer, dimension, nlist)
```

### Caching Strategies

```python
# Enable query result caching
coordinator = AgenticRagCoordinator(knowledge_store)
coordinator.enable_caching = True
coordinator.cache_ttl = 3600  # 1 hour
```

## Monitoring and Analytics

### Query Analytics

```python
# Get query history and performance
stats = rag_coordinator.get_stats()

print(f"Total queries: {stats['total_queries']}")
print(f"Agent usage: {stats['agent_usage']}")
print(f"Average confidence: {stats['average_confidence']:.2f}")
```

### Knowledge Store Monitoring

```python
# Monitor knowledge growth
stats = knowledge_store.get_stats()

print(f"Total chunks: {stats['total_chunks']}")
print(f"Sources: {stats['unique_sources']}")
print(f"Vector index size: {stats['faiss_vectors']}")
```

### Real-time Metrics

```python
# Track ingestion rates
pipeline_stats = {
    'chunks_per_minute': ingested_count / (time_elapsed / 60),
    'average_chunk_size': total_content_length / ingested_count,
    'embedding_time': embedding_duration
}
```

## Integration Patterns

### With Blackboard Pattern

The RAG system integrates seamlessly with the blackboard coordination pattern:

1. **Automatic Knowledge Capture**: RAG agent subscribes to blackboard messages and automatically ingests prediction results, explanations, and market data
2. **Enhanced Workflows**: Predictions can include RAG-powered analysis alongside standard explanations
3. **Cross-Agent Learning**: Knowledge from one prediction improves future predictions

### With MCP Integration

```python
# MCP tool that uses RAG for enhanced responses
async def rag_enhanced_prediction(vehicle_age, mileage):
    # Standard prediction
    prediction = await predict_vehicle_price(vehicle_age, mileage)
    
    # RAG analysis
    rag_query = f"Analyze pricing for {vehicle_age}y vehicle with {mileage}km"
    rag_result = await rag_coordinator.process_query(rag_query)
    
    return {
        **prediction,
        'rag_analysis': rag_result['response']
    }
```

### With Ollama Enhancement

```python
# Combine RAG retrieval with Ollama generation
class OllamaEnhancedRagAgent(RagAgent):
    def __init__(self, knowledge_store, ollama_agent):
        super().__init__("ollama_rag", knowledge_store)
        self.ollama_agent = ollama_agent
    
    async def process_query(self, query, context=None):
        # Retrieve relevant knowledge
        chunks = self.knowledge_store.search_hybrid(query)
        
        # Use Ollama to generate enhanced response
        if self.ollama_agent.is_available():
            prompt = f"Based on this knowledge: {chunks}, answer: {query}"
            response = self.ollama_agent.generate_response(prompt)
            return {'response': response, 'enhanced': True}
        
        # Fallback to standard RAG
        return await super().process_query(query, context)
```

## Configuration

### Environment Variables

```bash
# RAG system configuration
RAG_KNOWLEDGE_STORE_PATH=knowledge_store.db
RAG_EMBEDDING_MODEL=all-MiniLM-L6-v2
RAG_VECTOR_DIMENSION=384
RAG_CHUNK_SIZE=500
RAG_CHUNK_OVERLAP=50

# Search configuration
RAG_VECTOR_WEIGHT=0.7
RAG_TEXT_WEIGHT=0.3
RAG_SEARCH_THRESHOLD=0.5
RAG_MAX_RESULTS=10

# Performance settings
RAG_ENABLE_CACHING=true
RAG_CACHE_TTL=3600
RAG_BACKGROUND_INGESTION=true
```

### Advanced Configuration

```python
# Custom RAG configuration
class RagConfig:
    def __init__(self):
        self.knowledge_store_path = "advanced_knowledge.db"
        self.embedding_model = "all-mpnet-base-v2"  # Higher quality
        self.chunk_strategies = {
            'documents': 'semantic',
            'data': 'structured',
            'explanations': 'paragraph'
        }
        self.search_weights = {
            'vector': 0.8,
            'text': 0.2
        }
        self.agent_specializations = {
            'vehicle_analysis': ['pricing', 'depreciation', 'features'],
            'market_analysis': ['trends', 'economic', 'seasonal'],
            'comparative_analysis': ['competition', 'alternatives']
        }

# Initialize with custom config
config = RagConfig()
knowledge_store = KnowledgeStore(config.knowledge_store_path, config.embedding_model)
```

## Security and Privacy

### Data Protection

1. **Local Storage**: All knowledge stored locally in SQLite
2. **No External APIs**: Embeddings generated locally (optional)
3. **Access Control**: Database-level permissions
4. **Data Retention**: Configurable cleanup policies

### Privacy Considerations

```python
# Anonymize sensitive data before ingestion
def anonymize_vehicle_data(record):
    return {
        'vehicle_type': record['brand'] + '_' + record['model'][:1],  # Partial model
        'age_range': f"{record['age']//2*2}-{record['age']//2*2+1}",  # Age ranges
        'mileage_range': f"{record['mileage']//10000*10000}+",        # Mileage bands
        'price_range': f"{record['price']//5000*5000}-{record['price']//5000*5000+4999}"
    }
```

## Troubleshooting

### Common Issues

#### 1. Embedding Model Loading Fails
```bash
# Solution: Install sentence-transformers
pip install sentence-transformers

# Or use basic text search
RAG_EMBEDDING_MODEL=none
```

#### 2. FAISS Not Available
```bash
# Solution: Install FAISS
pip install faiss-cpu  # For CPU-only
# or
pip install faiss-gpu  # For GPU support
```

#### 3. Poor Search Results
```python
# Debug search quality
results = knowledge_store.search_hybrid("test query", top_k=20)
for i, chunk in enumerate(results[:5]):
    print(f"{i+1}. Score: {chunk.relevance_score:.3f}")
    print(f"   Content: {chunk.content[:100]}...")
    print(f"   Source: {chunk.source}")
```

#### 4. Slow Performance
```python
# Optimize chunk size and overlap
pipeline = KnowledgeIngestionPipeline(knowledge_store)
# Reduce chunk size for faster processing
chunks = pipeline._chunk_fixed_size(content, chunk_size=200, overlap=20)
```

### Debug Mode

```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Monitor RAG operations
logger = logging.getLogger('agentic_rag')
logger.setLevel(logging.DEBUG)
```

## Future Enhancements

### Planned Features

1. **Advanced Chunking**
   - Semantic-aware content splitting
   - Document structure preservation
   - Multi-modal content support (images, tables)

2. **Enhanced Search**
   - Fuzzy matching capabilities
   - Contextual re-ranking
   - Multi-query fusion

3. **Agent Specialization**
   - Domain-specific embedding models
   - Expert system integration
   - Hierarchical knowledge organization

4. **Performance Optimization**
   - Distributed vector search
   - Incremental index updates
   - Intelligent caching strategies

### Research Directions

1. **Continual Learning**: Agents that improve from user feedback
2. **Explainable RAG**: Detailed reasoning paths for retrieved knowledge
3. **Multimodal RAG**: Integration of text, images, and structured data
4. **Federated RAG**: Distributed knowledge across multiple sources

## Contributing

When contributing to the Agentic RAG system:

1. **Follow RAG best practices** for chunking and retrieval
2. **Add comprehensive tests** for new agents and capabilities
3. **Document knowledge schemas** for new data types
4. **Consider privacy implications** of stored knowledge
5. **Optimize for performance** at scale
6. **Maintain backward compatibility** with existing workflows

## Integration Examples

### Complete System Integration

```python
# Full system with all patterns
async def comprehensive_vehicle_analysis():
    # Initialize all components
    workflow = VehiclePriceWorkflowCoordinator(
        use_ollama=True,    # Local LLM enhancement
        enable_rag=True     # Knowledge retrieval
    )
    
    # MCP agent for standardized interfaces
    mcp_agent = VehiclePriceAgent(model, features, mcp_enabled=True)
    
    workflow.start()
    
    try:
        # Multi-pattern prediction
        results = await asyncio.gather(
            # Blackboard coordination with RAG
            workflow.predict_price(3, 45000, include_rag_analysis=True),
            
            # Direct RAG query
            workflow.query_knowledge("Compare this to similar vehicles"),
            
            # MCP tool call
            mcp_agent.handle_mcp_tool_call("predict_vehicle_price", {
                "vehicle_age": 3, "mileage": 45000
            })
        )
        
        return {
            'coordinated_result': results[0],
            'rag_analysis': results[1],
            'mcp_result': results[2],
            'integration_complete': True
        }
        
    finally:
        workflow.stop()
```

This comprehensive integration provides:
- **Coordinated agents** working through blackboard pattern
- **Intelligent knowledge retrieval** with RAG capabilities
- **Local LLM enhancement** with Ollama integration
- **Standardized interfaces** through MCP protocol
- **Rich analytics and monitoring** across all components

The Agentic RAG pattern significantly enhances the system's ability to learn from experience, provide contextual insights, and deliver more accurate and explainable predictions.
