from src.data_loader import merge_data
from src.model import train_model
from src.agent import VehiclePriceAgent
from src.retriever import RetrieverAgent
from src.explainer import explain_prediction

def main():
    # Load and train model
    df = merge_data()
    model, metrics = train_model(df)
    feature_names = df.drop(columns=["price", "date"]).columns.tolist()

    # Initialize agents
    predictor = VehiclePriceAgent(model, feature_names)
    retriever = RetrieverAgent()

    # Input vehicle data
    vehicle_info = {"vehicle_age": 3, "mileage": 40000}

    # Fetch real-time market data (simulated)
    market_info = retriever.get_market_data()
    print("Market Data Retrieved:", market_info)

    # Predict vehicle price
    processed_input = predictor.perceive(vehicle_info, market_info)
    predicted_price = predictor.decide(processed_input)
    print(f"Recommended price: ${predicted_price:,.2f}")

    # Generate explanation using LLM
    combined_input = {**vehicle_info, **market_info}
    explanation = explain_prediction(combined_input, predicted_price)
    print("Explanation from AI agent:")
    print(explanation)

if __name__ == "__main__":
    main()
