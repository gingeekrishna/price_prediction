import sqlite3
from datetime import datetime

class LoggerAgent:
    def log(self, input_data: dict, predicted_price: float):
        conn = sqlite3.connect("predictions.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO predictions (vehicle_age, mileage, predicted_price, timestamp)
            VALUES (?, ?, ?, ?)
        """, (
            input_data["vehicle_age"],
            input_data["mileage"],
            predicted_price,
            datetime.now().isoformat()
        ))
        conn.commit()
        conn.close()
