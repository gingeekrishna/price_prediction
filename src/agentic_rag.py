"""
Agentic RAG (Retrieval-Augmented Generation) Pattern Implementation

This module implements an advanced RAG system with agentic capabilities for the 
Vehicle Price Prediction system. It combines database storage, vector search,
and intelligent agents for enhanced knowledge retrieval and generation.
"""

import asyncio
import json
import logging
import sqlite3
import numpy as np
import pickle
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
import hashlib
import os
import re
from abc import ABC, abstractmethod

# Vector search capabilities
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("FAISS not available. Vector search will be limited.")

# Embeddings
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    print("SentenceTransformers not available. Using basic text matching.")

logger = logging.getLogger(__name__)


@dataclass
class KnowledgeChunk:
    """A chunk of knowledge with metadata."""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[np.ndarray] = None
    created_at: datetime = None
    updated_at: datetime = None
    source: str = "unknown"
    chunk_type: str = "text"
    relevance_score: float = 0.0
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        result = asdict(self)
        result['embedding'] = self.embedding.tolist() if self.embedding is not None else None
        result['created_at'] = self.created_at.isoformat()
        result['updated_at'] = self.updated_at.isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeChunk':
        """Create from dictionary."""
        data = data.copy()
        if data.get('embedding'):
            data['embedding'] = np.array(data['embedding'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)


class KnowledgeStore:
    """
    Database-backed knowledge store with vector search capabilities.
    
    Provides persistent storage for knowledge chunks with metadata,
    vector embeddings, and full-text search capabilities.
    """
    
    def __init__(self, db_path: str = "knowledge_store.db", embedding_model: str = "all-MiniLM-L6-v2"):
        self.db_path = db_path
        self.embedding_model_name = embedding_model
        self.embedding_model = None
        self.faiss_index = None
        self.chunk_id_map = {}  # Maps FAISS indices to chunk IDs
        
        # Initialize database
        self._init_database()
        
        # Initialize embedding model if available
        if EMBEDDINGS_AVAILABLE:
            try:
                self.embedding_model = SentenceTransformer(embedding_model)
                logger.info(f"Loaded embedding model: {embedding_model}")
            except Exception as e:
                logger.warning(f"Failed to load embedding model: {e}")
        
        # Load existing FAISS index if available
        self._load_faiss_index()
    
    def _init_database(self):
        """Initialize the SQLite database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_chunks (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    embedding BLOB,
                    created_at TEXT,
                    updated_at TEXT,
                    source TEXT,
                    chunk_type TEXT,
                    relevance_score REAL DEFAULT 0.0
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_source ON knowledge_chunks(source)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_chunk_type ON knowledge_chunks(chunk_type)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_created_at ON knowledge_chunks(created_at)
            """)
            
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_fts USING fts5(
                    id, content, metadata, source
                )
            """)
            
            logger.info("Knowledge store database initialized")
    
    def _load_faiss_index(self):
        """Load existing FAISS index from disk."""
        index_path = self.db_path.replace('.db', '_faiss.index')
        map_path = self.db_path.replace('.db', '_faiss_map.pkl')
        
        if os.path.exists(index_path) and os.path.exists(map_path) and FAISS_AVAILABLE:
            try:
                self.faiss_index = faiss.read_index(index_path)
                with open(map_path, 'rb') as f:
                    self.chunk_id_map = pickle.load(f)
                logger.info(f"Loaded FAISS index with {self.faiss_index.ntotal} vectors")
            except Exception as e:
                logger.warning(f"Failed to load FAISS index: {e}")
    
    def _save_faiss_index(self):
        """Save FAISS index to disk."""
        if self.faiss_index is None or not FAISS_AVAILABLE:
            return
        
        index_path = self.db_path.replace('.db', '_faiss.index')
        map_path = self.db_path.replace('.db', '_faiss_map.pkl')
        
        try:
            faiss.write_index(self.faiss_index, index_path)
            with open(map_path, 'wb') as f:
                pickle.dump(self.chunk_id_map, f)
            logger.debug("FAISS index saved to disk")
        except Exception as e:
            logger.error(f"Failed to save FAISS index: {e}")
    
    def add_chunk(self, chunk: KnowledgeChunk) -> bool:
        """Add a knowledge chunk to the store."""
        try:
            # Generate embedding if model is available
            if self.embedding_model and chunk.embedding is None:
                chunk.embedding = self.embedding_model.encode(chunk.content)
            
            # Store in database
            with sqlite3.connect(self.db_path) as conn:
                # Serialize metadata and embedding
                metadata_json = json.dumps(chunk.metadata)
                embedding_blob = chunk.embedding.tobytes() if chunk.embedding is not None else None
                
                conn.execute("""
                    INSERT OR REPLACE INTO knowledge_chunks 
                    (id, content, metadata, embedding, created_at, updated_at, source, chunk_type, relevance_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    chunk.id,
                    chunk.content,
                    metadata_json,
                    embedding_blob,
                    chunk.created_at.isoformat(),
                    chunk.updated_at.isoformat(),
                    chunk.source,
                    chunk.chunk_type,
                    chunk.relevance_score
                ))
                
                # Add to FTS index
                conn.execute("""
                    INSERT OR REPLACE INTO knowledge_fts (id, content, metadata, source)
                    VALUES (?, ?, ?, ?)
                """, (chunk.id, chunk.content, metadata_json, chunk.source))
            
            # Add to FAISS index
            if chunk.embedding is not None and FAISS_AVAILABLE:
                self._add_to_faiss_index(chunk.id, chunk.embedding)
            
            logger.debug(f"Added knowledge chunk: {chunk.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add knowledge chunk: {e}")
            return False
    
    def _add_to_faiss_index(self, chunk_id: str, embedding: np.ndarray):
        """Add embedding to FAISS index."""
        if not FAISS_AVAILABLE:
            return
        
        try:
            # Initialize FAISS index if needed
            if self.faiss_index is None:
                dimension = embedding.shape[0]
                self.faiss_index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
            
            # Normalize embedding for cosine similarity
            embedding = embedding.reshape(1, -1)
            faiss.normalize_L2(embedding)
            
            # Add to index
            index_id = self.faiss_index.ntotal
            self.faiss_index.add(embedding)
            self.chunk_id_map[index_id] = chunk_id
            
        except Exception as e:
            logger.error(f"Failed to add embedding to FAISS index: {e}")
    
    def search_by_vector(self, query_embedding: np.ndarray, top_k: int = 10, threshold: float = 0.5) -> List[KnowledgeChunk]:
        """Search for similar chunks using vector similarity."""
        if not FAISS_AVAILABLE or self.faiss_index is None:
            return []
        
        try:
            # Normalize query embedding
            query_embedding = query_embedding.reshape(1, -1)
            faiss.normalize_L2(query_embedding)
            
            # Search
            scores, indices = self.faiss_index.search(query_embedding, top_k)
            
            # Retrieve matching chunks
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if score >= threshold and idx in self.chunk_id_map:
                    chunk_id = self.chunk_id_map[idx]
                    chunk = self.get_chunk(chunk_id)
                    if chunk:
                        chunk.relevance_score = float(score)
                        results.append(chunk)
            
            return results
            
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
    
    def search_by_text(self, query: str, top_k: int = 10) -> List[KnowledgeChunk]:
        """Search for chunks using full-text search."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT id, content, metadata, source, 
                           rank() OVER (ORDER BY rank) as relevance
                    FROM knowledge_fts 
                    WHERE knowledge_fts MATCH ? 
                    ORDER BY rank 
                    LIMIT ?
                """, (query, top_k))
                
                results = []
                for row in cursor.fetchall():
                    chunk = self.get_chunk(row[0])
                    if chunk:
                        chunk.relevance_score = 1.0 / (1.0 + row[4])  # Convert rank to score
                        results.append(chunk)
                
                return results
                
        except Exception as e:
            logger.error(f"Text search failed: {e}")
            return []
    
    def search_hybrid(self, query: str, top_k: int = 10, vector_weight: float = 0.7) -> List[KnowledgeChunk]:
        """Combine vector and text search for better results."""
        results = {}
        
        # Vector search
        if self.embedding_model:
            query_embedding = self.embedding_model.encode(query)
            vector_results = self.search_by_vector(query_embedding, top_k)
            for chunk in vector_results:
                results[chunk.id] = chunk
                chunk.relevance_score *= vector_weight
        
        # Text search
        text_results = self.search_by_text(query, top_k)
        for chunk in text_results:
            if chunk.id in results:
                # Combine scores
                results[chunk.id].relevance_score += chunk.relevance_score * (1 - vector_weight)
            else:
                chunk.relevance_score *= (1 - vector_weight)
                results[chunk.id] = chunk
        
        # Sort by combined relevance score
        sorted_results = sorted(results.values(), key=lambda x: x.relevance_score, reverse=True)
        return sorted_results[:top_k]
    
    def get_chunk(self, chunk_id: str) -> Optional[KnowledgeChunk]:
        """Retrieve a specific chunk by ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT id, content, metadata, embedding, created_at, updated_at, 
                           source, chunk_type, relevance_score
                    FROM knowledge_chunks 
                    WHERE id = ?
                """, (chunk_id,))
                
                row = cursor.fetchone()
                if row:
                    chunk_data = {
                        'id': row[0],
                        'content': row[1],
                        'metadata': json.loads(row[2]) if row[2] else {},
                        'created_at': datetime.fromisoformat(row[4]),
                        'updated_at': datetime.fromisoformat(row[5]),
                        'source': row[6],
                        'chunk_type': row[7],
                        'relevance_score': row[8]
                    }
                    
                    # Deserialize embedding
                    if row[3]:
                        embedding_bytes = row[3]
                        embedding_array = np.frombuffer(embedding_bytes, dtype=np.float32)
                        chunk_data['embedding'] = embedding_array
                    
                    return KnowledgeChunk(**chunk_data)
                
        except Exception as e:
            logger.error(f"Failed to retrieve chunk {chunk_id}: {e}")
        
        return None
    
    def get_chunks_by_source(self, source: str, limit: int = 100) -> List[KnowledgeChunk]:
        """Get all chunks from a specific source."""
        chunks = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT id FROM knowledge_chunks 
                    WHERE source = ? 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (source, limit))
                
                for row in cursor.fetchall():
                    chunk = self.get_chunk(row[0])
                    if chunk:
                        chunks.append(chunk)
                        
        except Exception as e:
            logger.error(f"Failed to retrieve chunks by source: {e}")
        
        return chunks
    
    def delete_chunk(self, chunk_id: str) -> bool:
        """Delete a chunk from the store."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM knowledge_chunks WHERE id = ?", (chunk_id,))
                conn.execute("DELETE FROM knowledge_fts WHERE id = ?", (chunk_id,))
                # Note: FAISS index cleanup would require rebuilding the entire index
            
            logger.debug(f"Deleted knowledge chunk: {chunk_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete chunk {chunk_id}: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge store."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM knowledge_chunks")
                total_chunks = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT COUNT(DISTINCT source) FROM knowledge_chunks")
                unique_sources = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT source, COUNT(*) FROM knowledge_chunks GROUP BY source")
                source_stats = dict(cursor.fetchall())
                
            return {
                'total_chunks': total_chunks,
                'unique_sources': unique_sources,
                'source_breakdown': source_stats,
                'faiss_vectors': self.faiss_index.ntotal if self.faiss_index else 0,
                'embedding_model': self.embedding_model_name,
                'embeddings_available': EMBEDDINGS_AVAILABLE,
                'faiss_available': FAISS_AVAILABLE
            }
            
        except Exception as e:
            logger.error(f"Failed to get knowledge store stats: {e}")
            return {}
    
    def close(self):
        """Close the knowledge store and save indices."""
        self._save_faiss_index()


class RagAgent(ABC):
    """Abstract base class for RAG agents."""
    
    def __init__(self, name: str, knowledge_store: KnowledgeStore):
        self.name = name
        self.knowledge_store = knowledge_store
    
    @abstractmethod
    async def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a query and return results."""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return a list of agent capabilities."""
        pass


class VehiclePriceRagAgent(RagAgent):
    """
    RAG agent specialized for vehicle price prediction queries.
    
    This agent can retrieve relevant information about vehicle pricing,
    market trends, and provide contextual responses.
    """
    
    def __init__(self, knowledge_store: KnowledgeStore):
        super().__init__("vehicle_price_rag", knowledge_store)
        self.capabilities = [
            "vehicle_price_analysis",
            "market_trend_analysis", 
            "feature_importance_explanation",
            "historical_data_retrieval",
            "comparative_analysis"
        ]
    
    async def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process vehicle price related queries."""
        try:
            # Analyze query intent
            intent = self._analyze_query_intent(query)
            
            # Retrieve relevant knowledge
            relevant_chunks = await self._retrieve_knowledge(query, intent)
            
            # Generate response based on retrieved knowledge
            response = await self._generate_response(query, relevant_chunks, context)
            
            return {
                'query': query,
                'intent': intent,
                'relevant_chunks': len(relevant_chunks),
                'response': response,
                'sources': [chunk.source for chunk in relevant_chunks],
                'confidence': self._calculate_confidence(relevant_chunks)
            }
            
        except Exception as e:
            logger.error(f"RAG query processing failed: {e}")
            return {
                'query': query,
                'error': str(e),
                'response': "I'm sorry, I couldn't process your query at this time."
            }
    
    def _analyze_query_intent(self, query: str) -> str:
        """Analyze the intent of the user query."""
        query_lower = query.lower()
        
        if any(term in query_lower for term in ['price', 'cost', 'value', 'worth']):
            if any(term in query_lower for term in ['predict', 'estimate', 'forecast']):
                return 'price_prediction'
            else:
                return 'price_inquiry'
        
        elif any(term in query_lower for term in ['market', 'trend', 'demand']):
            return 'market_analysis'
        
        elif any(term in query_lower for term in ['explain', 'why', 'how', 'factor']):
            return 'explanation'
        
        elif any(term in query_lower for term in ['compare', 'vs', 'versus', 'difference']):
            return 'comparison'
        
        elif any(term in query_lower for term in ['history', 'historical', 'past', 'previous']):
            return 'historical_analysis'
        
        else:
            return 'general_inquiry'
    
    async def _retrieve_knowledge(self, query: str, intent: str) -> List[KnowledgeChunk]:
        """Retrieve relevant knowledge chunks based on query and intent."""
        # Use hybrid search for best results
        chunks = self.knowledge_store.search_hybrid(query, top_k=10)
        
        # Filter chunks based on intent if needed
        if intent == 'market_analysis':
            chunks = [c for c in chunks if 'market' in c.metadata.get('tags', [])]
        elif intent == 'price_prediction':
            chunks = [c for c in chunks if 'prediction' in c.metadata.get('tags', [])]
        elif intent == 'historical_analysis':
            chunks = [c for c in chunks if 'historical' in c.metadata.get('tags', [])]
        
        return chunks[:5]  # Return top 5 most relevant
    
    async def _generate_response(self, query: str, chunks: List[KnowledgeChunk], context: Dict[str, Any] = None) -> str:
        """Generate a response based on retrieved knowledge."""
        if not chunks:
            return "I don't have specific information about that. Could you please provide more details or rephrase your question?"
        
        # Combine relevant content
        relevant_content = []
        for chunk in chunks:
            relevant_content.append(f"From {chunk.source}: {chunk.content}")
        
        # For now, return a structured response based on the retrieved content
        # In a production system, this would use an LLM to generate a more natural response
        
        response = f"Based on the available information:\n\n"
        
        for i, chunk in enumerate(chunks[:3], 1):
            response += f"{i}. {chunk.content[:200]}...\n"
            if chunk.metadata.get('price_range'):
                response += f"   Price range: {chunk.metadata['price_range']}\n"
            response += f"   Source: {chunk.source}\n\n"
        
        if context and 'predicted_price' in context:
            response += f"Current prediction: ${context['predicted_price']:.2f}\n"
        
        return response
    
    def _calculate_confidence(self, chunks: List[KnowledgeChunk]) -> float:
        """Calculate confidence score based on retrieved chunks."""
        if not chunks:
            return 0.0
        
        # Average relevance score
        avg_score = sum(chunk.relevance_score for chunk in chunks) / len(chunks)
        
        # Factor in number of chunks (more chunks = higher confidence, up to a point)
        count_factor = min(len(chunks) / 5.0, 1.0)
        
        return avg_score * count_factor
    
    def get_capabilities(self) -> List[str]:
        """Return agent capabilities."""
        return self.capabilities.copy()


class MarketTrendRagAgent(RagAgent):
    """RAG agent specialized for market trend analysis."""
    
    def __init__(self, knowledge_store: KnowledgeStore):
        super().__init__("market_trend_rag", knowledge_store)
        self.capabilities = [
            "market_trend_analysis",
            "seasonal_pattern_analysis",
            "economic_indicator_analysis",
            "demand_supply_analysis"
        ]
    
    async def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process market trend queries."""
        # Search for market-related knowledge
        chunks = self.knowledge_store.search_hybrid(query, top_k=8)
        market_chunks = [c for c in chunks if 'market' in c.chunk_type or 'trend' in c.metadata.get('tags', [])]
        
        if not market_chunks:
            return {
                'query': query,
                'response': "I don't have specific market trend information for your query.",
                'confidence': 0.0
            }
        
        # Analyze trends from retrieved data
        trends = self._analyze_trends(market_chunks)
        
        response = self._format_trend_response(trends, query)
        
        return {
            'query': query,
            'trends': trends,
            'response': response,
            'confidence': self._calculate_confidence(market_chunks),
            'data_points': len(market_chunks)
        }
    
    def _analyze_trends(self, chunks: List[KnowledgeChunk]) -> Dict[str, Any]:
        """Analyze trends from knowledge chunks."""
        trends = {
            'direction': 'stable',
            'strength': 'moderate',
            'key_factors': [],
            'time_period': 'recent'
        }
        
        # Simple trend analysis based on content keywords
        content_text = ' '.join([chunk.content for chunk in chunks]).lower()
        
        if any(term in content_text for term in ['increase', 'rising', 'up', 'higher']):
            trends['direction'] = 'upward'
        elif any(term in content_text for term in ['decrease', 'falling', 'down', 'lower']):
            trends['direction'] = 'downward'
        
        # Extract key factors mentioned
        factors = ['fuel price', 'demand', 'supply', 'economy', 'interest rates', 'inflation']
        for factor in factors:
            if factor in content_text:
                trends['key_factors'].append(factor)
        
        return trends
    
    def _format_trend_response(self, trends: Dict[str, Any], query: str) -> str:
        """Format trend analysis into readable response."""
        response = f"Market trend analysis for your query:\n\n"
        response += f"Direction: {trends['direction'].title()}\n"
        response += f"Strength: {trends['strength'].title()}\n"
        
        if trends['key_factors']:
            response += f"Key factors: {', '.join(trends['key_factors'])}\n"
        
        return response
    
    def get_capabilities(self) -> List[str]:
        return self.capabilities.copy()


class AgenticRagCoordinator:
    """
    Coordinator for multiple RAG agents with intelligent routing.
    
    This coordinator manages multiple specialized RAG agents and routes
    queries to the most appropriate agent based on query analysis.
    """
    
    def __init__(self, knowledge_store: KnowledgeStore):
        self.knowledge_store = knowledge_store
        self.agents: Dict[str, RagAgent] = {}
        self.query_history = []
        
        # Initialize specialized agents
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all RAG agents."""
        self.agents['vehicle_price'] = VehiclePriceRagAgent(self.knowledge_store)
        self.agents['market_trend'] = MarketTrendRagAgent(self.knowledge_store)
        
        logger.info(f"Initialized {len(self.agents)} RAG agents")
    
    def register_agent(self, agent: RagAgent):
        """Register a new RAG agent."""
        self.agents[agent.name] = agent
        logger.info(f"Registered RAG agent: {agent.name}")
    
    async def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Route query to appropriate agent and return response."""
        try:
            # Determine best agent for the query
            best_agent = self._route_query(query)
            
            # Process query with selected agent
            result = await best_agent.process_query(query, context)
            
            # Add routing information
            result['selected_agent'] = best_agent.name
            result['available_agents'] = list(self.agents.keys())
            
            # Store query history
            self.query_history.append({
                'query': query,
                'agent': best_agent.name,
                'timestamp': datetime.now(),
                'confidence': result.get('confidence', 0.0)
            })
            
            # Keep only recent history
            if len(self.query_history) > 100:
                self.query_history = self.query_history[-100:]
            
            return result
            
        except Exception as e:
            logger.error(f"RAG query processing failed: {e}")
            return {
                'query': query,
                'error': str(e),
                'response': "I encountered an error processing your query."
            }
    
    def _route_query(self, query: str) -> RagAgent:
        """Determine the best agent for processing the query."""
        query_lower = query.lower()
        
        # Simple routing logic based on keywords
        if any(term in query_lower for term in ['market', 'trend', 'demand', 'supply', 'economic']):
            return self.agents['market_trend']
        else:
            return self.agents['vehicle_price']  # Default to vehicle price agent
    
    def get_agent_capabilities(self) -> Dict[str, List[str]]:
        """Get capabilities of all registered agents."""
        return {name: agent.get_capabilities() for name, agent in self.agents.items()}
    
    def get_query_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent query history."""
        return self.query_history[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get coordinator statistics."""
        agent_usage = {}
        for entry in self.query_history:
            agent = entry['agent']
            agent_usage[agent] = agent_usage.get(agent, 0) + 1
        
        return {
            'total_queries': len(self.query_history),
            'agent_usage': agent_usage,
            'average_confidence': sum(e.get('confidence', 0) for e in self.query_history) / len(self.query_history) if self.query_history else 0,
            'knowledge_store_stats': self.knowledge_store.get_stats()
        }


class KnowledgeIngestionPipeline:
    """
    Pipeline for ingesting various types of knowledge into the RAG system.
    
    Supports ingestion from multiple sources including files, databases,
    APIs, and structured data.
    """
    
    def __init__(self, knowledge_store: KnowledgeStore):
        self.knowledge_store = knowledge_store
        self.chunking_strategies = {
            'fixed_size': self._chunk_fixed_size,
            'sentence': self._chunk_by_sentence,
            'paragraph': self._chunk_by_paragraph,
            'semantic': self._chunk_semantic
        }
    
    async def ingest_text_data(self, content: str, source: str, 
                             chunk_strategy: str = 'paragraph',
                             metadata: Dict[str, Any] = None) -> int:
        """Ingest text data into the knowledge store."""
        if metadata is None:
            metadata = {}
        
        # Add ingestion metadata
        metadata.update({
            'ingested_at': datetime.now().isoformat(),
            'content_length': len(content),
            'chunk_strategy': chunk_strategy
        })
        
        # Chunk the content
        chunks = self.chunking_strategies[chunk_strategy](content)
        
        # Create knowledge chunks
        ingested_count = 0
        for i, chunk_text in enumerate(chunks):
            chunk_id = self._generate_chunk_id(source, i, chunk_text)
            
            chunk = KnowledgeChunk(
                id=chunk_id,
                content=chunk_text,
                metadata=metadata.copy(),
                source=source,
                chunk_type='text'
            )
            
            if self.knowledge_store.add_chunk(chunk):
                ingested_count += 1
        
        logger.info(f"Ingested {ingested_count} chunks from {source}")
        return ingested_count
    
    async def ingest_vehicle_data(self, vehicle_records: List[Dict[str, Any]], source: str = "vehicle_database") -> int:
        """Ingest structured vehicle data."""
        ingested_count = 0
        
        for record in vehicle_records:
            # Convert vehicle record to text description
            content = self._vehicle_record_to_text(record)
            
            chunk_id = self._generate_chunk_id(source, record.get('id', ingested_count), content)
            
            chunk = KnowledgeChunk(
                id=chunk_id,
                content=content,
                metadata={
                    'record_type': 'vehicle_data',
                    'vehicle_age': record.get('age'),
                    'mileage': record.get('mileage'),
                    'price': record.get('price'),
                    'brand': record.get('brand'),
                    'model': record.get('model'),
                    'tags': ['vehicle', 'structured_data']
                },
                source=source,
                chunk_type='structured_data'
            )
            
            if self.knowledge_store.add_chunk(chunk):
                ingested_count += 1
        
        logger.info(f"Ingested {ingested_count} vehicle records")
        return ingested_count
    
    async def ingest_market_data(self, market_records: List[Dict[str, Any]], source: str = "market_database") -> int:
        """Ingest market data."""
        ingested_count = 0
        
        for record in market_records:
            content = self._market_record_to_text(record)
            
            chunk_id = self._generate_chunk_id(source, record.get('date', ingested_count), content)
            
            chunk = KnowledgeChunk(
                id=chunk_id,
                content=content,
                metadata={
                    'record_type': 'market_data',
                    'date': record.get('date'),
                    'market_index': record.get('market_index'),
                    'fuel_price': record.get('fuel_price'),
                    'tags': ['market', 'economic_data']
                },
                source=source,
                chunk_type='market_data'
            )
            
            if self.knowledge_store.add_chunk(chunk):
                ingested_count += 1
        
        logger.info(f"Ingested {ingested_count} market records")
        return ingested_count
    
    def _chunk_fixed_size(self, content: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Chunk content into fixed-size pieces with overlap."""
        chunks = []
        start = 0
        
        while start < len(content):
            end = start + chunk_size
            chunk = content[start:end]
            
            # Try to end at word boundary
            if end < len(content):
                last_space = chunk.rfind(' ')
                if last_space > chunk_size * 0.8:  # If we can find a reasonable word boundary
                    chunk = chunk[:last_space]
                    end = start + last_space
            
            chunks.append(chunk.strip())
            start = end - overlap
        
        return [c for c in chunks if c]  # Remove empty chunks
    
    def _chunk_by_sentence(self, content: str) -> List[str]:
        """Chunk content by sentences."""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', content)
        return [s.strip() for s in sentences if s.strip()]
    
    def _chunk_by_paragraph(self, content: str) -> List[str]:
        """Chunk content by paragraphs."""
        paragraphs = content.split('\n\n')
        return [p.strip() for p in paragraphs if p.strip()]
    
    def _chunk_semantic(self, content: str) -> List[str]:
        """Semantic chunking (simplified version)."""
        # For now, use paragraph chunking as a proxy for semantic chunking
        # In a production system, this would use more sophisticated NLP techniques
        return self._chunk_by_paragraph(content)
    
    def _vehicle_record_to_text(self, record: Dict[str, Any]) -> str:
        """Convert vehicle record to descriptive text."""
        parts = []
        
        if record.get('brand') and record.get('model'):
            parts.append(f"{record['brand']} {record['model']}")
        
        if record.get('age'):
            parts.append(f"aged {record['age']} years")
        
        if record.get('mileage'):
            parts.append(f"with {record['mileage']:,} km mileage")
        
        if record.get('price'):
            parts.append(f"priced at ${record['price']:,.2f}")
        
        description = "Vehicle: " + ", ".join(parts)
        
        if record.get('features'):
            description += f". Features: {', '.join(record['features'])}"
        
        return description
    
    def _market_record_to_text(self, record: Dict[str, Any]) -> str:
        """Convert market record to descriptive text."""
        parts = []
        
        if record.get('date'):
            parts.append(f"On {record['date']}")
        
        if record.get('market_index'):
            parts.append(f"market index was {record['market_index']}")
        
        if record.get('fuel_price'):
            parts.append(f"fuel price was ${record['fuel_price']:.2f}")
        
        description = "Market data: " + ", ".join(parts)
        
        if record.get('trend'):
            description += f". Trend: {record['trend']}"
        
        return description
    
    def _generate_chunk_id(self, source: str, identifier: Any, content: str) -> str:
        """Generate a unique chunk ID."""
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"{source}_{identifier}_{content_hash}"


# Integration with blackboard pattern
class BlackboardRagAgent:
    """Integration of RAG capabilities with the blackboard pattern."""
    
    def __init__(self, rag_coordinator: AgenticRagCoordinator):
        self.rag_coordinator = rag_coordinator
        self.name = "rag_agent"
    
    async def handle_rag_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle RAG queries for the blackboard system."""
        return await self.rag_coordinator.process_query(query, context)
    
    def get_knowledge_stats(self) -> Dict[str, Any]:
        """Get knowledge store statistics."""
        return self.rag_coordinator.get_stats()


# Example usage and testing
if __name__ == "__main__":
    async def test_rag_system():
        # Initialize knowledge store
        knowledge_store = KnowledgeStore("test_rag.db")
        
        # Initialize ingestion pipeline
        pipeline = KnowledgeIngestionPipeline(knowledge_store)
        
        # Sample data ingestion
        sample_text = """
        Vehicle depreciation is a key factor in price prediction. Typically, 
        vehicles lose 15-25% of their value in the first year and continue 
        to depreciate at a rate of 10-15% annually thereafter. Market conditions 
        significantly impact these rates.
        """
        
        await pipeline.ingest_text_data(
            sample_text, 
            "pricing_guide",
            metadata={'topic': 'depreciation', 'tags': ['pricing', 'depreciation']}
        )
        
        # Initialize RAG coordinator
        rag_coordinator = AgenticRagCoordinator(knowledge_store)
        
        # Test queries
        queries = [
            "How does vehicle age affect pricing?",
            "What are the current market trends?",
            "Explain vehicle depreciation factors"
        ]
        
        for query in queries:
            print(f"\nQuery: {query}")
            result = await rag_coordinator.process_query(query)
            print(f"Agent: {result['selected_agent']}")
            print(f"Response: {result['response']}")
            print(f"Confidence: {result.get('confidence', 0):.2f}")
        
        # Print stats
        stats = rag_coordinator.get_stats()
        print(f"\nRAG System Stats: {stats}")
        
        knowledge_store.close()
    
    # Run test
    import asyncio
    asyncio.run(test_rag_system())
