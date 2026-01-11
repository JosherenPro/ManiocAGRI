import sys
import os
import pandas as pd
from datetime import datetime, timedelta

# Add app directory to path
sys.path.append(os.path.join(os.getcwd(), "app"))

try:
    from app.core.ai_service import DemandPredictor

    print("=== Testing DemandPredictor ===")

    # Scenario 1: Not enough data
    print("\n[Test 1] Predicting with insufficient data...")
    not_enough_data = [
        {"created_at": datetime.now(), "total_price": 100},
        {"created_at": datetime.now(), "total_price": 200}
    ]
    result1 = DemandPredictor.predict(not_enough_data)
    print(f"Result: {result1}")
    if "Pas assez de données" in result1.get("msg", ""):
        print("✅ PASS: Correctly identified insufficient data.")
    else:
        print("❌ FAIL: Did not handle insufficient data correctly.")


    # Scenario 2: Sufficient data (mocking 10 days of orders)
    print("\n[Test 2] Predicting with sufficient historical data...")
    mock_data = []
    base_date = datetime.now() - timedelta(days=20)
    
    # Create a linear trend: more orders as days pass
    for i in range(20):
        # Create 2 orders per day initially, increasing to 5
        num_orders = 2 + int(i * 0.2) 
        current_date = base_date + timedelta(days=i)
        
        for _ in range(num_orders):
            mock_data.append({
                "created_at": current_date,
                "total_price": 1500
            })

    result2 = DemandPredictor.predict(mock_data)
    
    if isinstance(result2, list):
        print(f"✅ PASS: Generated {len(result2)}-day forecast.")
        print("Forecast Preview:")
        for day in result2:
            print(f"  Date: {day['date']}, Predicted: {day['predicted_orders']}")
    else:
        print(f"❌ FAIL: Forecast generation failed. Result: {result2}")

except ImportError as e:
    print(f"Import Error: {e}")
    print("Ensure you are running from the 'backend' directory and dependencies are installed.")
except Exception as e:
    print(f"An error occurred: {e}")
