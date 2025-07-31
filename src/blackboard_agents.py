"""
Blackboard-enabled agents for the Vehicle Price Prediction system.

These agents extend the existing agents to participate in the blackboard
coordination system, enabling better communication and workflow management.
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

from .coordinator import (
    BlackboardAgent, BlackboardCoordinator, MessageType, Priority, 
    BlackboardMessage, WorkflowBuilder
)
from .agents.market_data_agent import MarketDataAgent
from .agents.model_agent import PriceModelAgent
from .agents.explainer_agent import ExplainerAgentRAG
from .agents.insight_agent import InsightAgent
from .agents.logger_agent import LoggerAgent

import logging
logger = logging.getLogger(__name__)


class BlackboardMarketAgent(BlackboardAgent):
    """Market data agent with blackboard coordination capabilities."""
    
    def __init__(self, coordinator: BlackboardCoordinator):
        super().__init__("market_agent", coordinator)
        self.market_agent = MarketDataAgent()
        self.last_market_data = None
        self.cache_duration = 300  # 5 minutes cache
        self.last_fetch_time = None
        
        # Subscribe to relevant message types
        self.subscribe_to(MessageType.MARKET_DATA)
        self.subscribe_to(MessageType.PREDICTION_REQUEST)
    
    def handle_message(self, message: BlackboardMessage):
        """Handle blackboard messages."""
        if message.message_type == MessageType.PREDICTION_REQUEST:
            self._handle_prediction_request(message)
        elif message.message_type == MessageType.MARKET_DATA:
            # Another agent requested market data
            if message.data.get('request_fresh', False):
                self._provide_fresh_market_data(message)
    
    def _handle_prediction_request(self, message: BlackboardMessage):
        """Provide market data for prediction requests."""
        try:
            # Check if we need fresh data
            now = datetime.now()
            need_fresh = (
                self.last_market_data is None or 
                self.last_fetch_time is None or
                (now - self.last_fetch_time).seconds > self.cache_duration
            )
            
            if need_fresh:
                logger.info("Fetching fresh market data")
                self.last_market_data = self.market_agent.fetch()
                self.last_fetch_time = now
            
            # Post market data to blackboard
            self.post_message(
                MessageType.MARKET_DATA,
                {
                    'market_data': self.last_market_data,
                    'fetched_at': self.last_fetch_time.isoformat(),
                    'request_id': message.id,
                    'cached': not need_fresh
                },
                Priority.HIGH,
                response_to=message.id
            )
            
            logger.debug(f"Market data provided for request {message.id}")
            
        except Exception as e:
            logger.error(f"Market agent error: {e}")
            self.post_message(
                MessageType.ERROR,
                {
                    'error': str(e),
                    'agent': self.name,
                    'request_id': message.id
                },
                Priority.HIGH,
                response_to=message.id
            )
    
    def _provide_fresh_market_data(self, message: BlackboardMessage):
        """Provide fresh market data on request."""
        try:
            fresh_data = self.market_agent.fetch()
            self.post_message(
                MessageType.MARKET_DATA,
                {
                    'market_data': fresh_data,
                    'fetched_at': datetime.now().isoformat(),
                    'request_id': message.id,
                    'cached': False
                },
                Priority.MEDIUM,
                response_to=message.id
            )
        except Exception as e:
            logger.error(f"Fresh market data fetch error: {e}")


class BlackboardPredictionAgent(BlackboardAgent):
    """Price prediction agent with blackboard coordination."""
    
    def __init__(self, coordinator: BlackboardCoordinator):
        super().__init__("prediction_agent", coordinator)
        self.model_agent = PriceModelAgent()
        
        # Subscribe to relevant message types
        self.subscribe_to(MessageType.PREDICTION_REQUEST)
        self.subscribe_to(MessageType.MARKET_DATA)
        
        # Track pending predictions waiting for market data
        self.pending_predictions = {}
    
    def handle_message(self, message: BlackboardMessage):
        """Handle blackboard messages."""
        if message.message_type == MessageType.PREDICTION_REQUEST:
            self._handle_prediction_request(message)
        elif message.message_type == MessageType.MARKET_DATA:
            self._handle_market_data(message)
    
    def _handle_prediction_request(self, message: BlackboardMessage):
        """Handle prediction requests."""
        try:
            vehicle_age = message.data.get('vehicle_age')
            mileage = message.data.get('mileage')
            
            if vehicle_age is None or mileage is None:
                raise ValueError("vehicle_age and mileage are required")
            
            # Store the request and wait for market data
            self.pending_predictions[message.id] = {
                'original_request': message,
                'vehicle_age': vehicle_age,
                'mileage': mileage,
                'requested_at': datetime.now()
            }
            
            # Request market data if not already provided
            market_data_messages = self.get_messages(
                MessageType.MARKET_DATA,
                since=datetime.now() - timedelta(minutes=5)
            )
            
            if not market_data_messages:
                # Request fresh market data
                self.post_message(
                    MessageType.MARKET_DATA,
                    {'request_fresh': True, 'for_prediction': message.id},
                    Priority.HIGH
                )
            else:
                # Use existing market data
                latest_market_data = market_data_messages[0]
                self._make_prediction(message.id, latest_market_data.data['market_data'])
                
        except Exception as e:
            logger.error(f"Prediction request error: {e}")
            self.post_message(
                MessageType.ERROR,
                {
                    'error': str(e),
                    'agent': self.name,
                    'request_id': message.id
                },
                Priority.HIGH,
                response_to=message.id
            )
    
    def _handle_market_data(self, message: BlackboardMessage):
        """Handle market data for pending predictions."""
        # Check if this market data is for any pending predictions
        for pred_id, pred_info in list(self.pending_predictions.items()):
            market_data = message.data.get('market_data')
            if market_data:
                self._make_prediction(pred_id, market_data)
                del self.pending_predictions[pred_id]
    
    def _make_prediction(self, request_id: str, market_data: Dict[str, Any]):
        """Make the actual prediction."""
        try:
            pred_info = self.pending_predictions.get(request_id)
            if not pred_info:
                return
            
            # Prepare full input for prediction
            full_input = {
                'vehicle_age': pred_info['vehicle_age'],
                'mileage': pred_info['mileage'],
                'market_index': market_data['market_index'],
                'fuel_price': market_data['fuel_price']
            }
            
            # Make prediction
            predicted_price = self.model_agent.predict(full_input)
            
            # Post prediction result
            self.post_message(
                MessageType.PREDICTION_RESULT,
                {
                    'predicted_price': predicted_price,
                    'input_data': full_input,
                    'market_data': market_data,
                    'request_id': request_id,
                    'model_version': getattr(self.model_agent, 'model_version', 'unknown')
                },
                Priority.HIGH,
                response_to=request_id
            )
            
            logger.info(f"Prediction completed for request {request_id}: ${predicted_price:.2f}")
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            self.post_message(
                MessageType.ERROR,
                {
                    'error': str(e),
                    'agent': self.name,
                    'request_id': request_id
                },
                Priority.HIGH,
                response_to=request_id
            )


class BlackboardExplainerAgent(BlackboardAgent):
    """Explanation agent with blackboard coordination."""
    
    def __init__(self, coordinator: BlackboardCoordinator, use_ollama: bool = False):
        super().__init__("explainer_agent", coordinator)
        self.explainer_agent = ExplainerAgentRAG(use_ollama=use_ollama)
        
        # Subscribe to prediction results to provide explanations
        self.subscribe_to(MessageType.PREDICTION_RESULT)
        self.subscribe_to(MessageType.EXPLANATION)
    
    def handle_message(self, message: BlackboardMessage):
        """Handle blackboard messages."""
        if message.message_type == MessageType.PREDICTION_RESULT:
            self._handle_prediction_result(message)
        elif message.message_type == MessageType.EXPLANATION:
            # Direct explanation request
            self._handle_explanation_request(message)
    
    def _handle_prediction_result(self, message: BlackboardMessage):
        """Automatically generate explanation for prediction results."""
        try:
            predicted_price = message.data.get('predicted_price')
            input_data = message.data.get('input_data', {})
            request_id = message.data.get('request_id')
            
            if predicted_price is not None and input_data:
                explanation = self.explainer_agent.explain(input_data, predicted_price)
                
                self.post_message(
                    MessageType.EXPLANATION,
                    {
                        'explanation': explanation,
                        'prediction_price': predicted_price,
                        'input_data': input_data,
                        'request_id': request_id,
                        'explanation_type': 'automatic'
                    },
                    Priority.MEDIUM,
                    response_to=message.id
                )
                
                logger.debug(f"Explanation generated for prediction {request_id}")
                
        except Exception as e:
            logger.error(f"Explanation generation error: {e}")
    
    def _handle_explanation_request(self, message: BlackboardMessage):
        """Handle direct explanation requests."""
        try:
            predicted_price = message.data.get('predicted_price')
            input_data = message.data.get('input_data', {})
            
            if predicted_price is not None and input_data:
                explanation = self.explainer_agent.explain(input_data, predicted_price)
                
                self.post_message(
                    MessageType.EXPLANATION,
                    {
                        'explanation': explanation,
                        'prediction_price': predicted_price,
                        'input_data': input_data,
                        'request_id': message.id,
                        'explanation_type': 'requested'
                    },
                    Priority.MEDIUM,
                    response_to=message.id
                )
                
        except Exception as e:
            logger.error(f"Explanation request error: {e}")


class BlackboardInsightAgent(BlackboardAgent):
    """Insight agent with blackboard coordination."""
    
    def __init__(self, coordinator: BlackboardCoordinator, use_ollama: bool = False):
        super().__init__("insight_agent", coordinator)
        self.insight_agent = InsightAgent(use_ollama=use_ollama)
        
        # Subscribe to explanations to provide insights
        self.subscribe_to(MessageType.EXPLANATION)
        self.subscribe_to(MessageType.INSIGHT)
    
    def handle_message(self, message: BlackboardMessage):
        """Handle blackboard messages."""
        if message.message_type == MessageType.EXPLANATION:
            self._handle_explanation(message)
        elif message.message_type == MessageType.INSIGHT:
            # Direct insight request
            self._handle_insight_request(message)
    
    def _handle_explanation(self, message: BlackboardMessage):
        """Generate insights based on explanations."""
        try:
            explanation = message.data.get('explanation')
            predicted_price = message.data.get('prediction_price')
            request_id = message.data.get('request_id')
            
            if explanation and predicted_price is not None:
                recommendation = self.insight_agent.recommend_action(predicted_price, explanation)
                
                self.post_message(
                    MessageType.INSIGHT,
                    {
                        'recommendation': recommendation,
                        'predicted_price': predicted_price,
                        'explanation': explanation,
                        'request_id': request_id,
                        'insight_type': 'automatic'
                    },
                    Priority.MEDIUM,
                    response_to=message.id
                )
                
                logger.debug(f"Insight generated for request {request_id}")
                
        except Exception as e:
            logger.error(f"Insight generation error: {e}")
    
    def _handle_insight_request(self, message: BlackboardMessage):
        """Handle direct insight requests."""
        try:
            predicted_price = message.data.get('predicted_price')
            explanation = message.data.get('explanation', '')
            
            if predicted_price is not None:
                recommendation = self.insight_agent.recommend_action(predicted_price, explanation)
                
                self.post_message(
                    MessageType.INSIGHT,
                    {
                        'recommendation': recommendation,
                        'predicted_price': predicted_price,
                        'explanation': explanation,
                        'request_id': message.id,
                        'insight_type': 'requested'
                    },
                    Priority.MEDIUM,
                    response_to=message.id
                )
                
        except Exception as e:
            logger.error(f"Insight request error: {e}")


class BlackboardLoggerAgent(BlackboardAgent):
    """Logger agent with blackboard coordination."""
    
    def __init__(self, coordinator: BlackboardCoordinator):
        super().__init__("logger_agent", coordinator)
        self.logger_agent = LoggerAgent()
        
        # Subscribe to all message types for comprehensive logging
        for msg_type in MessageType:
            self.subscribe_to(msg_type)
    
    def handle_message(self, message: BlackboardMessage):
        """Log all blackboard activity."""
        try:
            # Log the message activity
            log_data = {
                'message_id': message.id,
                'message_type': message.message_type.value,
                'sender': message.sender,
                'timestamp': message.timestamp.isoformat(),
                'priority': message.priority.value,
                'data_summary': self._summarize_data(message.data)
            }
            
            # Use existing logger agent functionality
            if message.message_type == MessageType.PREDICTION_RESULT:
                input_data = message.data.get('input_data', {})
                predicted_price = message.data.get('predicted_price')
                if input_data and predicted_price is not None:
                    self.logger_agent.log(input_data, predicted_price)
            
            # Also log to blackboard-specific log
            self._log_blackboard_activity(log_data)
            
        except Exception as e:
            logger.error(f"Logger agent error: {e}")
    
    def _summarize_data(self, data: Dict[str, Any]) -> str:
        """Create a summary of message data for logging."""
        if not data:
            return "No data"
        
        summary_items = []
        for key, value in data.items():
            if isinstance(value, dict):
                summary_items.append(f"{key}: {len(value)} items")
            elif isinstance(value, list):
                summary_items.append(f"{key}: {len(value)} items")
            else:
                str_value = str(value)
                if len(str_value) > 50:
                    str_value = str_value[:47] + "..."
                summary_items.append(f"{key}: {str_value}")
        
        return ", ".join(summary_items[:3])  # Limit to first 3 items
    
    def _log_blackboard_activity(self, log_data: Dict[str, Any]):
        """Log blackboard-specific activity."""
        try:
            import sqlite3
            import os
            
            # Use the same database as the logger agent
            db_path = os.path.join(os.path.dirname(__file__), "predictions.db")
            
            with sqlite3.connect(db_path) as conn:
                # Create blackboard activity table if it doesn't exist
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS blackboard_activity (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        message_id TEXT,
                        message_type TEXT,
                        sender TEXT,
                        timestamp TEXT,
                        priority TEXT,
                        data_summary TEXT,
                        logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Insert activity log
                conn.execute("""
                    INSERT INTO blackboard_activity 
                    (message_id, message_type, sender, timestamp, priority, data_summary)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    log_data['message_id'],
                    log_data['message_type'],
                    log_data['sender'],
                    log_data['timestamp'],
                    log_data['priority'],
                    log_data['data_summary']
                ))
                
        except Exception as e:
            logger.error(f"Blackboard activity logging error: {e}")


class BlackboardRagAgent(BlackboardAgent):
    """RAG agent with blackboard coordination capabilities."""
    
    def __init__(self, coordinator: BlackboardCoordinator, knowledge_store_path: str = "knowledge_store.db"):
        super().__init__("rag_agent", coordinator)
        
        # Initialize RAG system
        try:
            from .agentic_rag import KnowledgeStore, AgenticRagCoordinator, KnowledgeIngestionPipeline
            self.knowledge_store = KnowledgeStore(knowledge_store_path)
            self.rag_coordinator = AgenticRagCoordinator(self.knowledge_store)
            self.ingestion_pipeline = KnowledgeIngestionPipeline(self.knowledge_store)
            self.rag_available = True
            logger.info("RAG system initialized successfully")
        except Exception as e:
            logger.warning(f"RAG system initialization failed: {e}")
            self.rag_available = False
        
        # Subscribe to relevant message types
        self.subscribe_to(MessageType.PREDICTION_RESULT)
        self.subscribe_to(MessageType.EXPLANATION)
        self.subscribe_to(MessageType.MARKET_DATA)
    
    def handle_message(self, message: BlackboardMessage):
        """Handle blackboard messages with RAG capabilities."""
        if not self.rag_available:
            return
        
        try:
            # Ingest knowledge from blackboard messages
            asyncio.create_task(self._ingest_message_knowledge(message))
            
            # Handle RAG queries if present in message data
            if message.data.get('rag_query'):
                asyncio.create_task(self._handle_rag_query(message))
                
        except Exception as e:
            logger.error(f"RAG agent message handling error: {e}")
    
    async def _ingest_message_knowledge(self, message: BlackboardMessage):
        """Ingest knowledge from blackboard messages."""
        try:
            if message.message_type == MessageType.PREDICTION_RESULT:
                # Ingest prediction results as knowledge
                predicted_price = message.data.get('predicted_price')
                input_data = message.data.get('input_data', {})
                
                if predicted_price and input_data:
                    content = f"Vehicle prediction: {input_data.get('vehicle_age', 'unknown')} years old, " \
                             f"{input_data.get('mileage', 'unknown')} km mileage, " \
                             f"predicted price ${predicted_price:.2f}"
                    
                    await self.ingestion_pipeline.ingest_text_data(
                        content,
                        f"prediction_results_{message.sender}",
                        metadata={
                            'message_id': message.id,
                            'predicted_price': predicted_price,
                            'vehicle_age': input_data.get('vehicle_age'),
                            'mileage': input_data.get('mileage'),
                            'tags': ['prediction', 'results', 'vehicle_data']
                        }
                    )
            
            elif message.message_type == MessageType.EXPLANATION:
                # Ingest explanations as knowledge
                explanation = message.data.get('explanation')
                if explanation:
                    await self.ingestion_pipeline.ingest_text_data(
                        explanation,
                        f"explanations_{message.sender}",
                        metadata={
                            'message_id': message.id,
                            'explanation_type': message.data.get('explanation_type', 'automatic'),
                            'tags': ['explanation', 'reasoning', 'knowledge']
                        }
                    )
            
            elif message.message_type == MessageType.MARKET_DATA:
                # Ingest market data as knowledge
                market_data = message.data.get('market_data', {})
                if market_data:
                    content = f"Market conditions: index {market_data.get('market_index', 'unknown')}, " \
                             f"fuel price ${market_data.get('fuel_price', 'unknown')}"
                    
                    await self.ingestion_pipeline.ingest_text_data(
                        content,
                        f"market_data_{message.sender}",
                        metadata={
                            'message_id': message.id,
                            'market_index': market_data.get('market_index'),
                            'fuel_price': market_data.get('fuel_price'),
                            'tags': ['market', 'economic_data', 'trends']
                        }
                    )
                    
        except Exception as e:
            logger.error(f"Knowledge ingestion error: {e}")
    
    async def _handle_rag_query(self, message: BlackboardMessage):
        """Handle RAG queries from blackboard messages."""
        try:
            query = message.data.get('rag_query')
            context = message.data.get('context', {})
            
            # Process query with RAG system
            result = await self.rag_coordinator.process_query(query, context)
            
            # Post RAG response to blackboard
            self.post_message(
                MessageType.EXPLANATION,  # RAG responses are explanatory
                {
                    'rag_response': result['response'],
                    'query': query,
                    'confidence': result.get('confidence', 0.0),
                    'selected_agent': result.get('selected_agent'),
                    'relevant_chunks': result.get('relevant_chunks', 0),
                    'sources': result.get('sources', [])
                },
                Priority.MEDIUM,
                response_to=message.id
            )
            
        except Exception as e:
            logger.error(f"RAG query handling error: {e}")
    
    async def query_knowledge(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Direct knowledge query interface."""
        if not self.rag_available:
            return {'error': 'RAG system not available'}
        
        return await self.rag_coordinator.process_query(query, context)
    
    def get_knowledge_stats(self) -> Dict[str, Any]:
        """Get knowledge store statistics."""
        if not self.rag_available:
            return {'error': 'RAG system not available'}
        
        return self.rag_coordinator.get_stats()
    
    def stop(self):
        """Stop the RAG agent and close knowledge store."""
        if self.rag_available and hasattr(self, 'knowledge_store'):
            self.knowledge_store.close()
        super().stop()


class VehiclePriceWorkflowCoordinator:
    """
    High-level coordinator for vehicle price prediction workflows.
    
    This class orchestrates the complete prediction workflow using the
    blackboard pattern for agent coordination, now including RAG capabilities.
    """
    
    def __init__(self, use_ollama: bool = False, enable_rag: bool = True):
        self.coordinator = BlackboardCoordinator()
        self.use_ollama = use_ollama
        self.enable_rag = enable_rag
        
        # Initialize blackboard agents
        self.market_agent = BlackboardMarketAgent(self.coordinator)
        self.prediction_agent = BlackboardPredictionAgent(self.coordinator)
        self.explainer_agent = BlackboardExplainerAgent(self.coordinator, use_ollama)
        self.insight_agent = BlackboardInsightAgent(self.coordinator, use_ollama)
        self.logger_agent = BlackboardLoggerAgent(self.coordinator)
        
        # Initialize RAG agent if enabled
        self.rag_agent = None
        if enable_rag:
            try:
                self.rag_agent = BlackboardRagAgent(self.coordinator)
                logger.info("RAG agent initialized successfully")
            except Exception as e:
                logger.warning(f"RAG agent initialization failed: {e}")
        
        self.agents = [
            self.market_agent,
            self.prediction_agent,
            self.explainer_agent,
            self.insight_agent,
            self.logger_agent
        ]
        
        if self.rag_agent:
            self.agents.append(self.rag_agent)
        
        # Track active prediction requests
        self.active_requests = {}
    
    def start(self):
        """Start the workflow coordinator and all agents."""
        self.coordinator.start()
        
        for agent in self.agents:
            agent.start()
        
        logger.info("VehiclePriceWorkflowCoordinator started with RAG support")
    
    def stop(self):
        """Stop all agents and the coordinator."""
        for agent in self.agents:
            agent.stop()
        
        self.coordinator.stop()
        logger.info("VehiclePriceWorkflowCoordinator stopped")
    
    async def predict_price(self, vehicle_age: float, mileage: float, 
                          include_explanation: bool = True,
                          include_insights: bool = True,
                          include_rag_analysis: bool = True,
                          timeout: float = 30.0) -> Dict[str, Any]:
        """
        Make a complete price prediction with explanation, insights, and RAG analysis.
        
        This method initiates a coordinated workflow through the blackboard
        system and waits for the complete result.
        """
        request_id = f"pred_{int(time.time())}_{len(self.active_requests)}"
        
        # Post the initial prediction request
        message_id = self.coordinator.post_message(
            MessageType.PREDICTION_REQUEST,
            {
                'vehicle_age': vehicle_age,
                'mileage': mileage,
                'include_explanation': include_explanation,
                'include_insights': include_insights,
                'include_rag_analysis': include_rag_analysis and self.rag_agent is not None,
                'request_id': request_id
            },
            'workflow_coordinator',
            Priority.HIGH
        )
        
        # Track the request
        self.active_requests[request_id] = {
            'message_id': message_id,
            'started_at': datetime.now(),
            'status': 'started',
            'results': {}
        }
        
        # Wait for completion
        return await self._wait_for_completion(request_id, timeout, include_rag_analysis)
    
    async def query_knowledge(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Query the RAG system directly."""
        if not self.rag_agent:
            return {'error': 'RAG system not available'}
        
        return await self.rag_agent.query_knowledge(query, context)
    
    async def _wait_for_completion(self, request_id: str, timeout: float, include_rag: bool = False) -> Dict[str, Any]:
        """Wait for workflow completion and collect results."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Check for prediction result
            prediction_messages = self.coordinator.get_messages(
                MessageType.PREDICTION_RESULT,
                since=self.active_requests[request_id]['started_at']
            )
            
            prediction_result = None
            for msg in prediction_messages:
                if msg.data.get('request_id') == request_id:
                    prediction_result = msg.data
                    break
            
            if not prediction_result:
                await asyncio.sleep(0.1)
                continue
            
            # Get explanation if available
            explanation_messages = self.coordinator.get_messages(
                MessageType.EXPLANATION,
                since=self.active_requests[request_id]['started_at']
            )
            
            explanation = None
            rag_analysis = None
            for msg in explanation_messages:
                if msg.data.get('request_id') == request_id:
                    if msg.data.get('rag_response'):
                        rag_analysis = {
                            'response': msg.data.get('rag_response'),
                            'confidence': msg.data.get('confidence', 0.0),
                            'sources': msg.data.get('sources', []),
                            'relevant_chunks': msg.data.get('relevant_chunks', 0)
                        }
                    else:
                        explanation = msg.data.get('explanation')
            
            # Get insights if available
            insight_messages = self.coordinator.get_messages(
                MessageType.INSIGHT,
                since=self.active_requests[request_id]['started_at']
            )
            
            recommendation = None
            for msg in insight_messages:
                if msg.data.get('request_id') == request_id:
                    recommendation = msg.data.get('recommendation')
                    break
            
            # If RAG is enabled, try to get additional analysis
            if include_rag and self.rag_agent and not rag_analysis:
                try:
                    rag_query = f"Analyze vehicle pricing for {prediction_result['input_data']['vehicle_age']} year old vehicle with {prediction_result['input_data']['mileage']} km mileage"
                    rag_result = await self.rag_agent.query_knowledge(
                        rag_query, 
                        {'predicted_price': prediction_result['predicted_price']}
                    )
                    if 'error' not in rag_result:
                        rag_analysis = {
                            'response': rag_result.get('response', ''),
                            'confidence': rag_result.get('confidence', 0.0),
                            'sources': rag_result.get('sources', []),
                            'selected_agent': rag_result.get('selected_agent', '')
                        }
                except Exception as e:
                    logger.warning(f"RAG analysis failed: {e}")
            
            # Compile complete result
            result = {
                'request_id': request_id,
                'predicted_price': prediction_result['predicted_price'],
                'input_data': prediction_result['input_data'],
                'market_data': prediction_result['market_data'],
                'explanation': explanation,
                'recommendation': recommendation,
                'rag_analysis': rag_analysis,
                'processing_time': time.time() - start_time,
                'workflow_complete': True,
                'timestamp': datetime.now().isoformat(),
                'agents_used': [agent.name for agent in self.agents if agent._active]
            }
            
            # Clean up
            del self.active_requests[request_id]
            
            return result
        
        # Timeout occurred
        del self.active_requests[request_id]
        raise TimeoutError(f"Prediction workflow timeout after {timeout}s")
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get the current status of the workflow coordinator."""
        status = {
            'coordinator_active': self.coordinator._running,
            'active_requests': len(self.active_requests),
            'agents_status': {
                agent.name: agent._active for agent in self.agents
            },
            'blackboard_messages': len(self.coordinator.messages),
            'use_ollama': self.use_ollama,
            'enable_rag': self.enable_rag,
            'rag_available': self.rag_agent is not None
        }
        
        # Add RAG statistics if available
        if self.rag_agent:
            try:
                rag_stats = self.rag_agent.get_knowledge_stats()
                status['rag_stats'] = rag_stats
            except Exception as e:
                status['rag_error'] = str(e)
        
        return status


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        
        # Create and start workflow coordinator
        workflow = VehiclePriceWorkflowCoordinator(use_ollama=True)
        workflow.start()
        
        try:
            # Make a prediction
            result = await workflow.predict_price(
                vehicle_age=3,
                mileage=45000,
                include_explanation=True,
                include_insights=True
            )
            
            print("Prediction Result:")
            print(json.dumps(result, indent=2))
            
        finally:
            workflow.stop()
    
    # Run the example
    asyncio.run(main())
