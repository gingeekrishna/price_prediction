import sqlite3
import logging
import asyncio
import time
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel
from src.data_loader import merge_data
from src.model import train_model
from src.agent import VehiclePriceAgent
from src.retriever import RetrieverAgent
from src.explainer import explain_prediction

# For Html run (for frontend)
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

# For Cors
from fastapi.middleware.cors import CORSMiddleware

# For Database
import databases
import sqlalchemy

from fastapi.responses import JSONResponse

# Set up logging
logger = logging.getLogger(__name__)

from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse

# Adding agents into the api
from src.agents.market_data_agent import MarketDataAgent
from src.agents.model_agent import PriceModelAgent
from src.agents.explainer_agent import ExplainerAgentRAG
from src.agents.logger_agent import LoggerAgent

# from src.agents.market_data_agent import MarketDataAgent
from src.agents.insight_agent import InsightAgent

# Initialize Ollama agent (optional)
try:
    from src.agents.ollama_agent import OllamaAgent, get_ollama_agent
    OLLAMA_AVAILABLE = True
    ollama_agent = get_ollama_agent()
    if ollama_agent and ollama_agent.is_available():
        logging.info("Ollama agent initialized successfully")
    else:
        OLLAMA_AVAILABLE = False
        logging.info("Ollama agent not available")
except ImportError as e:
    OLLAMA_AVAILABLE = False
    logging.warning(f"Ollama not available: {e}")

# Initialize Claude agent (optional)
try:
    from src.agents.claude_agent import ClaudeAgent
    CLAUDE_AVAILABLE = True
    claude_agent = ClaudeAgent()
    if claude_agent and claude_agent.available:
        logging.info("Claude agent initialized successfully")
    else:
        CLAUDE_AVAILABLE = False
        logging.info("Claude agent not available - check ANTHROPIC_API_KEY")
except ImportError as e:
    CLAUDE_AVAILABLE = False
    logging.warning(f"Claude not available: {e}")

app = FastAPI(title="Vehicle Price Prediction API")

# Configure paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
db_path = os.path.join(project_root, "predictions.db")

DATABASE_URL = f"sqlite:///{db_path}"

#for database setup
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

predictions = sqlalchemy.Table(
    "predictions",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("vehicle_age", sqlalchemy.Integer),
    sqlalchemy.Column("mileage", sqlalchemy.Integer),
    sqlalchemy.Column("predicted_price", sqlalchemy.Float),
    sqlalchemy.Column("timestamp", sqlalchemy.DateTime),
)

engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)
   
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or use ["http://localhost:8000"] if more strict
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VehicleInput(BaseModel):
    vehicle_age: int
    mileage: int

# Initialize agents and model at startup
df = merge_data()
model, metrics = train_model(df)
feature_names = df.drop(columns=["price", "date"]).columns.tolist()

predictor = VehiclePriceAgent(model, feature_names)
retriever = RetrieverAgent()

#For Database configuration
@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
 

def run_agents(vehicle_info: dict):
    market_info = retriever.get_market_data()
    processed_input = predictor.perceive(vehicle_info, market_info)
    predicted_price = predictor.decide(processed_input)
    explanation = explain_prediction({**vehicle_info, **market_info}, predicted_price)
    return predicted_price, market_info, explanation

# @app.post("/predict")
# async def predict(vehicle: VehicleInput):
#     vehicle_data = vehicle.dict()
#     try:
#         price, market_data, explanation = run_agents(vehicle_data)
#         return {
#             "predicted_price": price,
#             "market_data": market_data,
#             "explanation": explanation
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/predict")
# async def predict(vehicle: VehicleInput):
#     vehicle_data = vehicle.dict()
#     try:
#         price, market_data, explanation = run_agents(vehicle_data)
#         # Log prediction
#         query = predictions.insert().values(
#             vehicle_age=vehicle_data["vehicle_age"],
#             mileage=vehicle_data["mileage"],
#             predicted_price=price,
#             timestamp=datetime.utcnow()
#         )
#         await database.execute(query)

#         return {
#             "predicted_price": price,
#             "market_data": market_data,
#             "explanation": explanation
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
@app.post("/predict")
async def predict(request: Request, payload: dict, response: Response):
    # Add cache-control headers to prevent caching
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    vehicle_age = payload.get("vehicle_age")
    mileage = payload.get("mileage")
    
    # Debug logging to see what values we're receiving
    print(f"DEBUG: Received payload: {payload}")
    print(f"DEBUG: vehicle_age: {vehicle_age}, mileage: {mileage}")

    # Agents
    market_agent = MarketDataAgent()
    model_agent = PriceModelAgent()
    explainer_agent = ExplainerAgentRAG()
    logger_agent = LoggerAgent()

    insight_agent = InsightAgent()
    market_data = market_agent.fetch()

    full_input = {
        "vehicle_age": vehicle_age,
        "mileage": mileage,
        "market_index": market_data["market_index"],
        "fuel_price": market_data["fuel_price"]
    }

    print(f"DEBUG: full_input sent to model: {full_input}")

    predicted_price = model_agent.predict(full_input)
    explanation = explainer_agent.explain(full_input, predicted_price)
    recommendation = insight_agent.recommend_action(predicted_price, explanation)
    logger_agent.log(full_input, predicted_price)

    return {
        "predicted_price": predicted_price,
        "explanation": explanation,
        "recommendation": recommendation,
        "market_data": market_data
    }
        
# @app.get("/")
# async def root():
#     return FileResponse(os.path.join("static", "index.html"))

# Original Jinja2 template route
@app.get("/old", response_class=HTMLResponse)
async def old_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# New Angular-style frontend route
@app.get("/", response_class=HTMLResponse)
async def angular_index():
    frontend_path = os.path.join(project_root, "frontend", "index.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path)
    else:
        # Fallback to old template if new frontend doesn't exist
        return FileResponse(os.path.join(project_root, "templates", "index.html"))

# Serve any static assets (if you add CSS/JS files later)
static_dir = os.path.join(project_root, "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Mount the frontend directory to serve static files
frontend_dir = os.path.join(project_root, "frontend")
if os.path.exists(frontend_dir):
    app.mount("/frontend", StaticFiles(directory=frontend_dir), name="frontend")

@app.get("/logs")
async def get_logs():
    query = "SELECT * FROM predictions ORDER BY timestamp DESC"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    # return {"logs": rows}
   
    logs = [
        {
            "id": row[0],
            "vehicle_age": row[1],
            "mileage": row[2],
            "predicted_price": row[3],
            "timestamp": row[4],
        }
        for row in rows
    ]
    return JSONResponse(content={"logs": logs})

templates_dir = os.path.join(project_root, "templates")
templates = Jinja2Templates(directory=templates_dir)

@app.get("/logs-view", response_class=HTMLResponse)
async def logs_view(request: Request):
    return templates.TemplateResponse("logs.html", {"request": request})

# Ollama Integration Endpoints

@app.post("/predict_with_ollama")
async def predict_with_ollama(request: Request, payload: dict, response: Response):
    """Enhanced prediction with Ollama-powered explanations and insights."""
    # Add cache-control headers to prevent caching
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    vehicle_age = payload.get("vehicle_age")
    mileage = payload.get("mileage")
    
    # Debug logging to see what values we're receiving
    print(f"DEBUG: Ollama prediction - vehicle_age: {vehicle_age}, mileage: {mileage}")

    # Initialize agents
    market_agent = MarketDataAgent()
    model_agent = PriceModelAgent()
    explainer_agent = ExplainerAgentRAG(use_ollama=True)  # Enable Ollama
    logger_agent = LoggerAgent()
    insight_agent = InsightAgent(use_ollama=True)  # Enable Ollama

    # Get market data and make prediction
    market_data = market_agent.fetch()
    full_input = {
        "vehicle_age": vehicle_age,
        "mileage": mileage,
        "market_index": market_data["market_index"],
        "fuel_price": market_data["fuel_price"]
    }

    predicted_price = model_agent.predict(full_input)
    
    # Generate enhanced explanation and insights using Ollama
    explanation = explainer_agent.explain(full_input, predicted_price)
    recommendation = insight_agent.recommend_action(predicted_price, explanation)
    
    # Log the prediction
    logger_agent.log(full_input, predicted_price)

    return {
        "predicted_price": predicted_price,
        "explanation": explanation,
        "recommendation": recommendation,
        "market_data": market_data,
        "ollama_enhanced": True,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/ollama/status")
async def ollama_status():
    """Check Ollama availability and current model."""
    if OLLAMA_AVAILABLE and ollama_agent:
        model_info = ollama_agent.get_model_info()
        available_models = ollama_agent.list_available_models()
        return {
            "available": True,
            "current_model": model_info["current_model"],
            "host": model_info["host"],
            "available_models": available_models,
            "status": "connected"
        }
    else:
        return {
            "available": False,
            "status": "not_connected",
            "message": "Ollama not available. Install Ollama and run 'ollama serve' to enable AI-enhanced features."
        }

@app.get("/ollama/models")
async def list_ollama_models():
    """List available Ollama models."""
    if OLLAMA_AVAILABLE and ollama_agent:
        models = ollama_agent.list_available_models()
        return {
            "models": models, 
            "current": ollama_agent.model_name,
            "count": len(models)
        }
    return {
        "error": "Ollama not available",
        "models": [],
        "current": None,
        "count": 0
    }

@app.post("/ollama/switch_model")
async def switch_ollama_model(model_name: str):
    """Switch Ollama model."""
    if OLLAMA_AVAILABLE and ollama_agent:
        success = ollama_agent.switch_model(model_name)
        return {
            "success": success, 
            "current_model": ollama_agent.model_name,
            "message": f"Switched to {model_name}" if success else f"Failed to switch to {model_name}"
        }
    return {
        "error": "Ollama not available",
        "success": False
    }

@app.post("/ollama/query")
async def ollama_natural_language_query(request: Request, payload: dict):
    """Handle natural language queries about vehicle pricing using Ollama."""
    if not OLLAMA_AVAILABLE or not ollama_agent:
        return {
            "error": "Ollama not available",
            "response": "Natural language queries require Ollama to be installed and running."
        }
    
    query = payload.get("query", "")
    context = payload.get("context", {})
    
    if not query:
        return {"error": "Query is required"}
    
    try:
        response_text = ollama_agent.natural_language_query(query, context)
        return {
            "query": query,
            "response": response_text,
            "model": ollama_agent.model_name,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "error": f"Query failed: {str(e)}",
            "query": query
        }

# Claude Integration Endpoints

@app.post("/predict_with_claude")
async def predict_with_claude(request: Request, payload: dict, response: Response):
    """Enhanced prediction with Claude-powered explanations and insights."""
    # Add cache-control headers to prevent caching
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    vehicle_age = payload.get("vehicle_age")
    mileage = payload.get("mileage")
    make = payload.get("make", "Unknown")
    model = payload.get("model", "Unknown")
    year = payload.get("year")
    
    # Debug logging
    print(f"DEBUG: Claude prediction - vehicle_age: {vehicle_age}, mileage: {mileage}")

    try:
        # Initialize agents
        market_agent = MarketDataAgent()
        model_agent = PriceModelAgent()
        
        # Use Claude-enabled explainer
        explainer_agent = ExplainerAgentRAG(use_claude=True, llm_provider="claude")
        
        # Collect market data
        market_data = market_agent.collect_market_data()
        print(f"DEBUG: Market data: {market_data}")
        
        # Make prediction
        input_data = {
            "vehicle_age": vehicle_age,
            "mileage": mileage,
            "market_index": market_data.get("market_index", 1000),
            "fuel_price": market_data.get("fuel_price", 3.5),
            "make": make,
            "model": model,
            "year": year
        }
        
        predicted_price = model_agent.predict_price(input_data)
        print(f"DEBUG: Predicted price: {predicted_price}")
        
        # Generate enhanced explanation using Claude
        explanation = explainer_agent.explain(input_data, predicted_price)
        
        # Generate recommendation
        recommendation = "💎 Premium AI analysis complete. Claude provides sophisticated market insights."
        
        # Log prediction to database
        log_data = {
            "vehicle_age": vehicle_age,
            "mileage": mileage,
            "predicted_price": predicted_price,
            "explanation": explanation,
            "llm_provider": "claude"
        }
        
        await database.execute(
            "INSERT INTO predictions (vehicle_age, mileage, predicted_price, explanation, timestamp) VALUES (:vehicle_age, :mileage, :predicted_price, :explanation, :timestamp)",
            {**log_data, "timestamp": datetime.now().isoformat()}
        )
        
        return {
            "predicted_price": predicted_price,
            "explanation": explanation,
            "recommendation": recommendation,
            "market_data": market_data,
            "llm_provider": "claude",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Error in Claude prediction: {str(e)}")
        return {
            "error": f"Prediction failed: {str(e)}",
            "llm_provider": "claude",
            "timestamp": datetime.now().isoformat()
        }

@app.get("/claude/status")
async def claude_status():
    """Check Claude availability."""
    if CLAUDE_AVAILABLE and claude_agent:
        return {
            "available": True,
            "model": claude_agent.model_name,
            "status": "connected",
            "provider": "Anthropic Claude"
        }
    else:
        return {
            "available": False,
            "status": "not_connected",
            "message": "Claude not available. Set ANTHROPIC_API_KEY environment variable to enable Claude AI features."
        }

@app.post("/predict_with_ai")
async def predict_with_ai(request: Request, payload: dict, response: Response):
    """Smart prediction that auto-selects the best available AI (Claude > Ollama > Standard)."""
    # Add cache-control headers
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    vehicle_age = payload.get("vehicle_age")
    mileage = payload.get("mileage")
    make = payload.get("make", "Unknown")
    model = payload.get("model", "Unknown")
    year = payload.get("year")
    
    try:
        # Initialize agents
        market_agent = MarketDataAgent()
        model_agent = PriceModelAgent()
        
        # Use smart explainer with auto LLM selection
        explainer_agent = ExplainerAgentRAG(
            use_claude=CLAUDE_AVAILABLE, 
            use_ollama=OLLAMA_AVAILABLE, 
            llm_provider="auto"
        )
        
        # Collect market data
        market_data = market_agent.collect_market_data()
        
        # Make prediction
        input_data = {
            "vehicle_age": vehicle_age,
            "mileage": mileage,
            "market_index": market_data.get("market_index", 1000),
            "fuel_price": market_data.get("fuel_price", 3.5),
            "make": make,
            "model": model,
            "year": year
        }
        
        predicted_price = model_agent.predict_price(input_data)
        
        # Generate smart explanation (tries Claude first, then Ollama, then standard)
        explanation = explainer_agent.explain(input_data, predicted_price)
        
        # Determine which AI was used
        ai_provider = "claude" if "Claude AI" in explanation else "ollama" if "Ollama AI" in explanation else "standard"
        
        return {
            "predicted_price": predicted_price,
            "explanation": explanation,
            "market_data": market_data,
            "ai_provider": ai_provider,
            "claude_available": CLAUDE_AVAILABLE,
            "ollama_available": OLLAMA_AVAILABLE,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "error": f"Smart prediction failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

# Blackboard Coordination Endpoints

@app.post("/predict_coordinated")
async def predict_with_coordination(request: Request, payload: dict, response: Response):
    """Enhanced prediction using blackboard coordination pattern."""
    # Add cache-control headers to prevent caching
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    vehicle_age = payload.get("vehicle_age")
    mileage = payload.get("mileage")
    include_explanation = payload.get("include_explanation", True)
    include_insights = payload.get("include_insights", True)
    
    # Debug logging
    print(f"DEBUG: Coordinated prediction - vehicle_age: {vehicle_age}, mileage: {mileage}")

    try:
        # Import blackboard workflow coordinator
        from .blackboard_agents import VehiclePriceWorkflowCoordinator
        
        # Create and start workflow coordinator
        workflow = VehiclePriceWorkflowCoordinator(use_ollama=OLLAMA_AVAILABLE)
        workflow.start()
        
        try:
            # Make coordinated prediction
            result = await workflow.predict_price(
                vehicle_age=vehicle_age,
                mileage=mileage,
                include_explanation=include_explanation,
                include_insights=include_insights,
                timeout=30.0
            )
            
            return {
                **result,
                "coordination_enabled": True,
                "agents_used": ["market", "prediction", "explainer", "insight", "logger"],
                "workflow_pattern": "blackboard"
            }
            
        finally:
            workflow.stop()
            
    except Exception as e:
        logger.error(f"Coordinated prediction error: {e}")
        return {
            "error": f"Coordinated prediction failed: {str(e)}",
            "coordination_enabled": False,
            "fallback_available": True
        }

@app.get("/blackboard/status")
async def blackboard_status():
    """Get blackboard system status."""
    try:
        from .blackboard_agents import VehiclePriceWorkflowCoordinator
        
        # Create temporary coordinator to check status
        workflow = VehiclePriceWorkflowCoordinator()
        status = workflow.get_workflow_status()
        
        return {
            "blackboard_available": True,
            "status": status,
            "pattern": "blackboard_coordination",
            "message": "Blackboard coordination system available"
        }
    except Exception as e:
        return {
            "blackboard_available": False,
            "error": str(e),
            "pattern": "standard",
            "message": "Blackboard coordination not available, using standard agents"
        }

@app.get("/blackboard/messages")
async def get_blackboard_messages(
    message_type: Optional[str] = None,
    sender: Optional[str] = None,
    limit: int = 50
):
    """Get recent blackboard messages for debugging/monitoring."""
    try:
        from .blackboard_agents import VehiclePriceWorkflowCoordinator
        from .coordinator import MessageType
        
        # Create temporary coordinator
        workflow = VehiclePriceWorkflowCoordinator()
        workflow.start()
        
        try:
            # Parse message type if provided
            msg_type = None
            if message_type:
                try:
                    msg_type = MessageType(message_type)
                except ValueError:
                    return {"error": f"Invalid message type: {message_type}"}
            
            # Get messages
            messages = workflow.coordinator.get_messages(
                message_type=msg_type,
                sender=sender,
                limit=limit
            )
            
            # Convert to JSON-serializable format
            message_data = [msg.to_dict() for msg in messages]
            
            return {
                "messages": message_data,
                "count": len(message_data),
                "total_messages": len(workflow.coordinator.messages),
                "active_agents": list(workflow.coordinator.agents.keys())
            }
            
        finally:
            workflow.stop()
            
    except Exception as e:
        return {
            "error": f"Failed to get blackboard messages: {str(e)}",
            "messages": [],
            "count": 0
        }

@app.post("/blackboard/workflow")
async def create_custom_workflow(payload: dict):
    """Create and execute a custom workflow using blackboard coordination."""
    try:
        from .blackboard_agents import VehiclePriceWorkflowCoordinator
        from .coordinator import WorkflowBuilder
        
        workflow_id = payload.get("workflow_id", f"custom_{int(time.time())}")
        steps = payload.get("steps", [])
        
        if not steps:
            return {"error": "Workflow steps are required"}
        
        # Create workflow coordinator
        coordinator_instance = VehiclePriceWorkflowCoordinator()
        coordinator_instance.start()
        
        try:
            # Build custom workflow
            builder = WorkflowBuilder(coordinator_instance.coordinator)
            
            for step in steps:
                builder.add_step(
                    step_name=step.get("name"),
                    agent_name=step.get("agent"),
                    action=step.get("action"),
                    dependencies=step.get("dependencies", []),
                    data=step.get("data", {})
                )
            
            # Execute workflow
            success = builder.execute(workflow_id)
            
            if success:
                # Wait a bit for workflow to process
                await asyncio.sleep(2)
                
                # Get workflow status
                status = coordinator_instance.coordinator.get_workflow_status(workflow_id)
                
                return {
                    "workflow_started": True,
                    "workflow_id": workflow_id,
                    "status": status,
                    "message": "Custom workflow executed successfully"
                }
            else:
                return {
                    "workflow_started": False,
                    "workflow_id": workflow_id,
                    "error": "Failed to start workflow"
                }
                
        finally:
            coordinator_instance.stop()
            
    except Exception as e:
        return {
            "error": f"Custom workflow error: {str(e)}",
            "workflow_started": False
        }

# RAG (Retrieval-Augmented Generation) Endpoints

@app.post("/rag/query")
async def rag_query(payload: dict):
    """Process natural language queries using the RAG system."""
    try:
        from .blackboard_agents import VehiclePriceWorkflowCoordinator
        
        query = payload.get("query", "")
        context = payload.get("context", {})
        
        if not query:
            return {"error": "Query is required"}
        
        # Create workflow coordinator with RAG enabled
        workflow = VehiclePriceWorkflowCoordinator(use_ollama=OLLAMA_AVAILABLE, enable_rag=True)
        workflow.start()
        
        try:
            # Query the RAG system
            result = await workflow.query_knowledge(query, context)
            
            return {
                "query": query,
                "response": result.get('response', ''),
                "confidence": result.get('confidence', 0.0),
                "sources": result.get('sources', []),
                "selected_agent": result.get('selected_agent', ''),
                "relevant_chunks": result.get('relevant_chunks', 0),
                "timestamp": datetime.now().isoformat(),
                "rag_enabled": True
            }
            
        finally:
            workflow.stop()
            
    except Exception as e:
        logger.error(f"RAG query error: {e}")
        return {
            "error": f"RAG query failed: {str(e)}",
            "query": payload.get("query", ""),
            "rag_enabled": False
        }

@app.post("/rag/ingest")
async def rag_ingest_data(payload: dict):
    """Ingest data into the RAG knowledge store."""
    try:
        from .agentic_rag import KnowledgeStore, KnowledgeIngestionPipeline
        
        content = payload.get("content", "")
        source = payload.get("source", "api_upload")
        chunk_strategy = payload.get("chunk_strategy", "paragraph")
        metadata = payload.get("metadata", {})
        
        if not content:
            return {"error": "Content is required"}
        
        # Initialize knowledge store and pipeline
        knowledge_store = KnowledgeStore()
        pipeline = KnowledgeIngestionPipeline(knowledge_store)
        
        try:
            # Ingest the content
            ingested_count = await pipeline.ingest_text_data(
                content, source, chunk_strategy, metadata
            )
            
            return {
                "success": True,
                "ingested_chunks": ingested_count,
                "source": source,
                "chunk_strategy": chunk_strategy,
                "content_length": len(content),
                "timestamp": datetime.now().isoformat()
            }
            
        finally:
            knowledge_store.close()
            
    except Exception as e:
        logger.error(f"RAG ingestion error: {e}")
        return {
            "error": f"RAG ingestion failed: {str(e)}",
            "success": False
        }

@app.get("/rag/knowledge/stats")
async def rag_knowledge_stats():
    """Get RAG knowledge store statistics."""
    try:
        from .agentic_rag import KnowledgeStore
        
        knowledge_store = KnowledgeStore()
        
        try:
            stats = knowledge_store.get_stats()
            return {
                "knowledge_stats": stats,
                "available": True,
                "timestamp": datetime.now().isoformat()
            }
            
        finally:
            knowledge_store.close()
            
    except Exception as e:
        logger.error(f"RAG stats error: {e}")
        return {
            "error": f"Failed to get RAG stats: {str(e)}",
            "available": False
        }

@app.get("/rag/knowledge/search")
async def rag_search_knowledge(
    query: str,
    search_type: str = "hybrid",
    limit: int = 10
):
    """Search the RAG knowledge store."""
    try:
        from .agentic_rag import KnowledgeStore
        
        if not query:
            return {"error": "Query parameter is required"}
        
        knowledge_store = KnowledgeStore()
        
        try:
            if search_type == "vector":
                if knowledge_store.embedding_model:
                    query_embedding = knowledge_store.embedding_model.encode(query)
                    results = knowledge_store.search_by_vector(query_embedding, limit)
                else:
                    return {"error": "Vector search not available - no embedding model"}
            elif search_type == "text":
                results = knowledge_store.search_by_text(query, limit)
            else:  # hybrid
                results = knowledge_store.search_hybrid(query, limit)
            
            # Convert results to JSON-serializable format
            search_results = []
            for chunk in results:
                search_results.append({
                    "id": chunk.id,
                    "content": chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content,
                    "source": chunk.source,
                    "chunk_type": chunk.chunk_type,
                    "relevance_score": chunk.relevance_score,
                    "metadata": chunk.metadata,
                    "created_at": chunk.created_at.isoformat()
                })
            
            return {
                "query": query,
                "search_type": search_type,
                "results": search_results,
                "count": len(search_results),
                "limit": limit,
                "timestamp": datetime.now().isoformat()
            }
            
        finally:
            knowledge_store.close()
            
    except Exception as e:
        logger.error(f"RAG search error: {e}")
        return {
            "error": f"RAG search failed: {str(e)}",
            "query": query,
            "results": []
        }

@app.post("/predict_rag_enhanced")
async def predict_with_rag_enhancement(request: Request, payload: dict, response: Response):
    """Enhanced prediction with RAG-powered analysis and insights."""
    # Add cache-control headers to prevent caching
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    vehicle_age = payload.get("vehicle_age")
    mileage = payload.get("mileage")
    include_rag_analysis = payload.get("include_rag_analysis", True)
    
    # Debug logging
    print(f"DEBUG: RAG-enhanced prediction - vehicle_age: {vehicle_age}, mileage: {mileage}")

    try:
        # Import workflow coordinator with RAG
        from .blackboard_agents import VehiclePriceWorkflowCoordinator
        
        # Create workflow coordinator with RAG enabled
        workflow = VehiclePriceWorkflowCoordinator(
            use_ollama=OLLAMA_AVAILABLE, 
            enable_rag=True
        )
        workflow.start()
        
        try:
            # Make RAG-enhanced prediction
            result = await workflow.predict_price(
                vehicle_age=vehicle_age,
                mileage=mileage,
                include_explanation=True,
                include_insights=True,
                include_rag_analysis=include_rag_analysis,
                timeout=45.0  # Longer timeout for RAG processing
            )
            
            return {
                **result,
                "rag_enhanced": True,
                "agents_used": result.get("agents_used", []),
                "workflow_pattern": "blackboard_with_rag"
            }
            
        finally:
            workflow.stop()
            
    except Exception as e:
        logger.error(f"RAG-enhanced prediction error: {e}")
        return {
            "error": f"RAG-enhanced prediction failed: {str(e)}",
            "rag_enhanced": False,
            "fallback_available": True
        }

@app.get("/health")
async def health_check():
    """Health check endpoint with all system status."""
    try:
        # Check blackboard system
        blackboard_status = False
        try:
            from .blackboard_agents import VehiclePriceWorkflowCoordinator
            workflow = VehiclePriceWorkflowCoordinator()
            blackboard_status = True
        except:
            pass
        
        # Check RAG system
        rag_status = False
        try:
            from .agentic_rag import KnowledgeStore
            knowledge_store = KnowledgeStore()
            knowledge_store.close()
            rag_status = True
        except:
            pass
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "api": "running",
                "database": "connected",
                "ollama": "available" if OLLAMA_AVAILABLE and ollama_agent and ollama_agent.is_available() else "unavailable",
                "blackboard": "available" if blackboard_status else "unavailable",
                "rag": "available" if rag_status else "unavailable",
                "mcp": "integrated"
            },
            "patterns_available": {
                "standard_agents": True,
                "blackboard_coordination": blackboard_status,
                "agentic_rag": rag_status,
                "mcp_integration": True,
                "ollama_enhancement": OLLAMA_AVAILABLE
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
