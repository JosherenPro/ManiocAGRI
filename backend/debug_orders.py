from app.core.db import engine
from sqlmodel import Session, select
from app.models.order import Order, OrderRead
from app.models.user import User
from typing import List
import json

def test_fetch_orders():
    with Session(engine) as session:
        # Find livreur1
        livreur = session.exec(select(User).where(User.username == 'livreur1')).first()
        if not livreur:
            print("Livreur1 not found")
            return
        
        print(f"Testing fetch for livreur: {livreur.username} (ID: {livreur.id})")
        
        try:
            statement = select(Order).where(Order.livreur_id == livreur.id)
            orders = session.exec(statement).all()
            print(f"Found {len(orders)} orders.")
            
            # Try to serialize like FastAPI does
            for o in orders:
                print(f"Order {o.id} data: {o.dict()}")
                print(f"Serializing order {o.id}...")
                processed = OrderRead.from_orm(o)
                # print(processed.json())
                print("Serialization successful.")
                
        except Exception as e:
            print(f"Error encountered: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_fetch_orders()
