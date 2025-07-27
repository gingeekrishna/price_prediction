import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.data_loader import merge_data
from src.model import train_model
from src.agent import VehiclePriceAgent
from src.retriever import RetrieverAgent
from src.explainer import explain_prediction

# For Html run (for frontend)
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# For Cors
from fastapi.middleware.cors import CORSMiddleware

# For Database
import databases
import sqlalchemy
from datetime import datetime

from fastapi.responses import JSONResponse

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

app = FastAPI(title="Vehicle Price Prediction API")

DATABASE_URL = "sqlite:///./predictions.db"

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
async def predict(request: Request, payload: dict):
    vehicle_age = payload.get("vehicle_age")
    mileage = payload.get("mileage")

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
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Serve any static assets (if you add CSS/JS files later)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/logs")
async def get_logs():
    query = "SELECT * FROM predictions ORDER BY timestamp DESC"
    conn = sqlite3.connect("predictions.db")
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

templates = Jinja2Templates(directory="templates")

@app.get("/logs-view", response_class=HTMLResponse)
async def logs_view(request: Request):
    return templates.TemplateResponse("logs.html", {"request": request})
