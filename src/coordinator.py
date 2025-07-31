"""
Blackboard/Coordinator Pattern Implementation for Vehicle Price Prediction System

This module implements the Blackboard architectural pattern where multiple agents
can share knowledge and coordinate through a central blackboard system.
"""

import asyncio
import json
import threading
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable, Set
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class Priority(Enum):
    """Priority levels for blackboard messages and tasks."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class MessageType(Enum):
    """Types of messages that can be posted to the blackboard."""
    PREDICTION_REQUEST = "prediction_request"
    MARKET_DATA = "market_data"
    PREDICTION_RESULT = "prediction_result"
    EXPLANATION = "explanation"
    INSIGHT = "insight"
    ERROR = "error"
    STATUS_UPDATE = "status_update"
    COORDINATION_REQUEST = "coordination_request"


@dataclass
class BlackboardMessage:
    """A message on the blackboard containing data and metadata."""
    id: str
    message_type: MessageType
    data: Dict[str, Any]
    sender: str
    timestamp: datetime
    priority: Priority = Priority.MEDIUM
    expires_at: Optional[datetime] = None
    processed_by: Set[str] = None
    requires_response: bool = False
    response_to: Optional[str] = None
    
    def __post_init__(self):
        if self.processed_by is None:
            self.processed_by = set()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        result['expires_at'] = self.expires_at.isoformat() if self.expires_at else None
        result['processed_by'] = list(self.processed_by)
        result['message_type'] = self.message_type.value
        result['priority'] = self.priority.value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BlackboardMessage':
        """Create from dictionary."""
        data = data.copy()
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        if data['expires_at']:
            data['expires_at'] = datetime.fromisoformat(data['expires_at'])
        data['processed_by'] = set(data['processed_by'])
        data['message_type'] = MessageType(data['message_type'])
        data['priority'] = Priority(data['priority'])
        return cls(**data)


class BlackboardCoordinator:
    """
    Central coordinator implementing the Blackboard pattern.
    
    The blackboard serves as a shared knowledge base where agents can:
    - Post messages and data
    - Subscribe to specific message types
    - Coordinate complex multi-agent workflows
    - Share state and intermediate results
    """
    
    def __init__(self, max_messages: int = 1000, cleanup_interval: int = 300):
        self.messages: Dict[str, BlackboardMessage] = {}
        self.subscribers: Dict[MessageType, List[Callable]] = {}
        self.agents: Dict[str, 'BlackboardAgent'] = {}
        self.max_messages = max_messages
        self.cleanup_interval = cleanup_interval
        self._lock = threading.RLock()
        self._message_counter = 0
        self._running = False
        self._cleanup_thread = None
        
        # Workflow coordination
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        self.workflow_callbacks: Dict[str, List[Callable]] = {}
        
        logger.info("BlackboardCoordinator initialized")
    
    def start(self):
        """Start the coordinator and cleanup processes."""
        self._running = True
        self._cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self._cleanup_thread.start()
        logger.info("BlackboardCoordinator started")
    
    def stop(self):
        """Stop the coordinator."""
        self._running = False
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=5)
        logger.info("BlackboardCoordinator stopped")
    
    def register_agent(self, agent: 'BlackboardAgent'):
        """Register an agent with the coordinator."""
        with self._lock:
            self.agents[agent.name] = agent
            logger.info(f"Agent '{agent.name}' registered with coordinator")
    
    def unregister_agent(self, agent_name: str):
        """Unregister an agent."""
        with self._lock:
            if agent_name in self.agents:
                del self.agents[agent_name]
                logger.info(f"Agent '{agent_name}' unregistered from coordinator")
    
    def subscribe(self, message_type: MessageType, callback: Callable[[BlackboardMessage], None]):
        """Subscribe to messages of a specific type."""
        with self._lock:
            if message_type not in self.subscribers:
                self.subscribers[message_type] = []
            self.subscribers[message_type].append(callback)
            logger.debug(f"New subscriber for {message_type.value}")
    
    def unsubscribe(self, message_type: MessageType, callback: Callable):
        """Unsubscribe from messages."""
        with self._lock:
            if message_type in self.subscribers:
                try:
                    self.subscribers[message_type].remove(callback)
                except ValueError:
                    pass
    
    def post_message(self, 
                    message_type: MessageType, 
                    data: Dict[str, Any], 
                    sender: str,
                    priority: Priority = Priority.MEDIUM,
                    expires_in_seconds: Optional[int] = None,
                    requires_response: bool = False,
                    response_to: Optional[str] = None) -> str:
        """Post a message to the blackboard."""
        with self._lock:
            self._message_counter += 1
            message_id = f"msg_{self._message_counter}_{int(time.time())}"
            
            expires_at = None
            if expires_in_seconds:
                expires_at = datetime.now() + timedelta(seconds=expires_in_seconds)
            
            message = BlackboardMessage(
                id=message_id,
                message_type=message_type,
                data=data,
                sender=sender,
                timestamp=datetime.now(),
                priority=priority,
                expires_at=expires_at,
                requires_response=requires_response,
                response_to=response_to
            )
            
            self.messages[message_id] = message
            
            # Trigger cleanup if we have too many messages
            if len(self.messages) > self.max_messages:
                self._cleanup_expired()
            
            logger.debug(f"Message {message_id} posted by {sender}: {message_type.value}")
            
            # Notify subscribers
            self._notify_subscribers(message)
            
            return message_id
    
    def get_messages(self, 
                    message_type: Optional[MessageType] = None, 
                    sender: Optional[str] = None,
                    since: Optional[datetime] = None,
                    limit: Optional[int] = None) -> List[BlackboardMessage]:
        """Retrieve messages from the blackboard with filtering."""
        with self._lock:
            messages = list(self.messages.values())
            
            # Apply filters
            if message_type:
                messages = [m for m in messages if m.message_type == message_type]
            if sender:
                messages = [m for m in messages if m.sender == sender]
            if since:
                messages = [m for m in messages if m.timestamp >= since]
            
            # Sort by priority and timestamp
            messages.sort(key=lambda m: (m.priority.value, m.timestamp), reverse=True)
            
            if limit:
                messages = messages[:limit]
            
            return messages
    
    def get_message(self, message_id: str) -> Optional[BlackboardMessage]:
        """Get a specific message by ID."""
        with self._lock:
            return self.messages.get(message_id)
    
    def mark_processed(self, message_id: str, agent_name: str):
        """Mark a message as processed by an agent."""
        with self._lock:
            if message_id in self.messages:
                self.messages[message_id].processed_by.add(agent_name)
                logger.debug(f"Message {message_id} marked as processed by {agent_name}")
    
    def start_workflow(self, workflow_id: str, workflow_data: Dict[str, Any], 
                      completion_callback: Optional[Callable] = None) -> bool:
        """Start a coordinated workflow."""
        with self._lock:
            if workflow_id in self.active_workflows:
                logger.warning(f"Workflow {workflow_id} already active")
                return False
            
            self.active_workflows[workflow_id] = {
                'id': workflow_id,
                'data': workflow_data,
                'status': 'started',
                'started_at': datetime.now(),
                'steps_completed': [],
                'current_step': workflow_data.get('first_step'),
                'completion_callback': completion_callback
            }
            
            # Post workflow start message
            self.post_message(
                MessageType.COORDINATION_REQUEST,
                {
                    'workflow_id': workflow_id,
                    'action': 'start',
                    'workflow_data': workflow_data
                },
                'coordinator',
                Priority.HIGH
            )
            
            logger.info(f"Workflow {workflow_id} started")
            return True
    
    def update_workflow_status(self, workflow_id: str, step: str, status: str, data: Dict[str, Any] = None):
        """Update the status of a workflow step."""
        with self._lock:
            if workflow_id not in self.active_workflows:
                logger.warning(f"Workflow {workflow_id} not found")
                return
            
            workflow = self.active_workflows[workflow_id]
            workflow['steps_completed'].append({
                'step': step,
                'status': status,
                'completed_at': datetime.now(),
                'data': data or {}
            })
            
            # Post status update
            self.post_message(
                MessageType.STATUS_UPDATE,
                {
                    'workflow_id': workflow_id,
                    'step': step,
                    'status': status,
                    'data': data
                },
                'coordinator',
                Priority.MEDIUM
            )
            
            logger.debug(f"Workflow {workflow_id} step '{step}' status: {status}")
    
    def complete_workflow(self, workflow_id: str, result: Dict[str, Any]):
        """Complete a workflow and trigger callbacks."""
        with self._lock:
            if workflow_id not in self.active_workflows:
                logger.warning(f"Workflow {workflow_id} not found")
                return
            
            workflow = self.active_workflows[workflow_id]
            workflow['status'] = 'completed'
            workflow['completed_at'] = datetime.now()
            workflow['result'] = result
            
            # Trigger callback if provided
            callback = workflow.get('completion_callback')
            if callback:
                try:
                    callback(workflow_id, result)
                except Exception as e:
                    logger.error(f"Workflow callback error: {e}")
            
            # Post completion message
            self.post_message(
                MessageType.STATUS_UPDATE,
                {
                    'workflow_id': workflow_id,
                    'action': 'complete',
                    'result': result
                },
                'coordinator',
                Priority.HIGH
            )
            
            # Clean up completed workflow after a delay
            threading.Timer(300, lambda: self._cleanup_workflow(workflow_id)).start()
            
            logger.info(f"Workflow {workflow_id} completed")
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a workflow."""
        with self._lock:
            return self.active_workflows.get(workflow_id)
    
    def _notify_subscribers(self, message: BlackboardMessage):
        """Notify all subscribers of a new message."""
        subscribers = self.subscribers.get(message.message_type, [])
        for callback in subscribers:
            try:
                # Run callback in a separate thread to avoid blocking
                threading.Thread(target=callback, args=(message,), daemon=True).start()
            except Exception as e:
                logger.error(f"Subscriber callback error: {e}")
    
    def _cleanup_expired(self):
        """Clean up expired messages."""
        now = datetime.now()
        expired_ids = []
        
        for msg_id, message in self.messages.items():
            if message.expires_at and message.expires_at <= now:
                expired_ids.append(msg_id)
        
        for msg_id in expired_ids:
            del self.messages[msg_id]
        
        if expired_ids:
            logger.debug(f"Cleaned up {len(expired_ids)} expired messages")
    
    def _cleanup_loop(self):
        """Background cleanup loop."""
        while self._running:
            try:
                time.sleep(self.cleanup_interval)
                if self._running:
                    self._cleanup_expired()
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
    
    def _cleanup_workflow(self, workflow_id: str):
        """Clean up a completed workflow."""
        with self._lock:
            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]
                logger.debug(f"Workflow {workflow_id} cleaned up")


class BlackboardAgent:
    """
    Base class for agents that participate in the blackboard system.
    
    Agents can post messages, subscribe to message types, and participate
    in coordinated workflows.
    """
    
    def __init__(self, name: str, coordinator: BlackboardCoordinator):
        self.name = name
        self.coordinator = coordinator
        self.subscriptions: List[MessageType] = []
        self._active = False
        
        # Register with coordinator
        self.coordinator.register_agent(self)
    
    def start(self):
        """Start the agent."""
        self._active = True
        logger.info(f"BlackboardAgent '{self.name}' started")
    
    def stop(self):
        """Stop the agent."""
        self._active = False
        # Unsubscribe from all message types
        for msg_type in self.subscriptions:
            self.coordinator.unsubscribe(msg_type, self._handle_message)
        self.coordinator.unregister_agent(self.name)
        logger.info(f"BlackboardAgent '{self.name}' stopped")
    
    def subscribe_to(self, message_type: MessageType):
        """Subscribe to a message type."""
        if message_type not in self.subscriptions:
            self.subscriptions.append(message_type)
            self.coordinator.subscribe(message_type, self._handle_message)
            logger.debug(f"Agent '{self.name}' subscribed to {message_type.value}")
    
    def post_message(self, message_type: MessageType, data: Dict[str, Any], 
                    priority: Priority = Priority.MEDIUM, **kwargs) -> str:
        """Post a message to the blackboard."""
        return self.coordinator.post_message(
            message_type, data, self.name, priority, **kwargs
        )
    
    def get_messages(self, message_type: Optional[MessageType] = None, **kwargs) -> List[BlackboardMessage]:
        """Get messages from the blackboard."""
        return self.coordinator.get_messages(message_type, **kwargs)
    
    def mark_processed(self, message_id: str):
        """Mark a message as processed."""
        self.coordinator.mark_processed(message_id, self.name)
    
    def _handle_message(self, message: BlackboardMessage):
        """Handle incoming messages. Override in subclasses."""
        if self._active and self.name not in message.processed_by:
            try:
                self.handle_message(message)
                self.mark_processed(message.id)
            except Exception as e:
                logger.error(f"Agent '{self.name}' message handling error: {e}")
    
    def handle_message(self, message: BlackboardMessage):
        """Override this method to handle specific messages."""
        logger.debug(f"Agent '{self.name}' received message: {message.message_type.value}")


# Workflow coordination utilities
class WorkflowBuilder:
    """Helper class for building complex workflows."""
    
    def __init__(self, coordinator: BlackboardCoordinator):
        self.coordinator = coordinator
        self.steps = []
        self.dependencies = {}
    
    def add_step(self, step_name: str, agent_name: str, action: str, 
                dependencies: List[str] = None, data: Dict[str, Any] = None):
        """Add a step to the workflow."""
        self.steps.append({
            'name': step_name,
            'agent': agent_name,
            'action': action,
            'data': data or {},
            'dependencies': dependencies or []
        })
        return self
    
    def build(self, workflow_id: str) -> Dict[str, Any]:
        """Build the workflow definition."""
        return {
            'id': workflow_id,
            'steps': self.steps,
            'first_step': self.steps[0]['name'] if self.steps else None
        }
    
    def execute(self, workflow_id: str, callback: Optional[Callable] = None) -> bool:
        """Execute the built workflow."""
        workflow_def = self.build(workflow_id)
        return self.coordinator.start_workflow(workflow_id, workflow_def, callback)


# Example usage and demonstration
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Create coordinator
    coordinator = BlackboardCoordinator()
    coordinator.start()
    
    try:
        # Example: Create a simple agent
        class ExampleAgent(BlackboardAgent):
            def handle_message(self, message: BlackboardMessage):
                print(f"Agent {self.name} handling: {message.message_type.value}")
                if message.message_type == MessageType.PREDICTION_REQUEST:
                    # Simulate processing
                    time.sleep(1)
                    # Post result
                    self.post_message(
                        MessageType.PREDICTION_RESULT,
                        {"result": "example_prediction", "input": message.data},
                        Priority.HIGH
                    )
        
        # Create and start agent
        agent = ExampleAgent("example_agent", coordinator)
        agent.subscribe_to(MessageType.PREDICTION_REQUEST)
        agent.start()
        
        # Post a test message
        coordinator.post_message(
            MessageType.PREDICTION_REQUEST,
            {"vehicle_age": 3, "mileage": 45000},
            "test_client"
        )
        
        # Wait for processing
        time.sleep(2)
        
        # Check results
        results = coordinator.get_messages(MessageType.PREDICTION_RESULT)
        print(f"Found {len(results)} results")
        
    finally:
        coordinator.stop()
