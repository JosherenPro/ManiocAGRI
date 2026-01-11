import sys
import os

# Add app directory to path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from sqlmodel import Session
# Import all models to register tables with SQLAlchemy
from models.user import User
from models.product import Product
from models.order import Order, OrderItem, OrderStatus
from core.db import engine
from datetime import datetime, timedelta
import random
import uuid

def inject_historical_orders():
    with Session(engine) as session:
        # Create orders spread over the last 10 days
        now = datetime.now()
        order_count = 0
        for i in range(1, 11):  # Go 1-10 days back
            date = now - timedelta(days=i)
            # 1 to 3 orders per day
            for _ in range(random.randint(1, 3)):
                order_number = f"HIST-{uuid.uuid4().hex[:8].upper()}"
                order = Order(
                    order_number=order_number,
                    client_id=1,  # Assuming user id 1 exists
                    client_name="Client Historique",
                    phone="90000000",
                    delivery_address="Lomé, Togo",
                    total_price=random.randint(5000, 20000),
                    status=OrderStatus.DELIVERED,
                    created_at=date
                )
                session.add(order)
                order_count += 1
        session.commit()
        print(f"Injected {order_count} historical orders!")

if __name__ == "__main__":
    inject_historical_orders()
