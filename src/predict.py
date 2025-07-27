import pandas as pd
from src.data_loader import merge_data
from src.model import train_model
from src.agent import VehiclePriceAgent

def main():
    # Load and merge data
    df = merge_data()
    print("Data loaded and merged:")
    print(df.head())

    # Train model
    model = train_model(df)

    # Setup agent
    agent = VehiclePriceAgent(model)

    # Prepare example input (drop target and date)
    example_input = df.drop(columns=["price", "date"]).iloc[:5]

    # Predict using agent
    preds = agent.predict(example_input)
    print("Predictions:")
    print(preds)

if __name__ == "__main__":
    main()
