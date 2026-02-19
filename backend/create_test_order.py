from app.core.db import engine, get_session
from sqlmodel import Session, select
from app.models.order import Order, OrderStatus
from app.models.user import User
import datetime

def create_test_order():
    with Session(engine) as session:
        # Find livreur1
        livreur = session.exec(select(User).where(User.username == 'livreur1')).first()
        if not livreur:
            print("Livreur1 not found")
            return
        
        # Create order
        order = Order(
            order_number=f"CMD-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
            client_name="Jean Dupont",
            phone="+228 90 00 00 00",
            delivery_address="Quartier Agoè, Lomé",
            status=OrderStatus.PENDING,
            total_price=5500,
            livreur_id=livreur.id
        )
        session.add(order)
        session.commit()
        session.refresh(order)
        
        # Add items
        from app.models.order import OrderItem
        from app.models.product import Product
        products = session.exec(select(Product).limit(2)).all()
        for p in products:
            item = OrderItem(
                order_id=order.id,
                product_id=p.id,
                product_name=p.name,
                quantity=2,
                unit_price=p.price
            )
            session.add(item)
        
        session.commit()
        print(f"Test order created: {order.order_number} with {len(products)} items assigned to {livreur.username}")

if __name__ == "__main__":
    create_test_order()
