import pandas as pd
from sklearn.linear_model import LinearRegression
import pickle
import os

# Simulated historical training data
data = {
    "vehicle_age": [1, 2, 3, 4, 5],
    "mileage": [10000, 30000, 40000, 60000, 80000],
    "market_index": [1100, 1110, 1090, 1130, 1080],
    "fuel_price": [3.2, 3.5, 3.7, 3.9, 4.0],
    "price": [22000, 19000, 17000, 15000, 13000]
}

df = pd.DataFrame(data)

X = df[["vehicle_age", "mileage", "market_index", "fuel_price"]]
y = df["price"]

model = LinearRegression()
model.fit(X, y)

# Save to src/model.pkl
model_path = os.path.join("src", "model.pkl")
with open(model_path, "wb") as f:
    pickle.dump(model, f)

print(f"✅ Model trained and saved to {model_path}")
