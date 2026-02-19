import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "app"))

from sqlmodel import Session, select
from core.db import engine
from models.product import Product
from models.user import User
from models.order import Order, OrderItem
from models.field_data import FieldData

def clean_catalog():
    # ID à supprimer: 3 (Gari), 14 (Farine de Manioc générique)
    # Remplaçants: 10 (Gari d'Or)
    
    with Session(engine) as session:
        # 1. Migrer les références de l'ID 3 vers l'ID 10
        order_items = session.exec(select(OrderItem).where(OrderItem.product_id == 3)).all()
        if order_items:
            print(f"Migration de {len(order_items)} lignes de commande de l'ID 3 vers l'ID 10")
            for item in order_items:
                item.product_id = 10
                session.add(item)
            session.flush()

        # 2. Supprimer les produits
        ids_to_delete = [3, 14]
        for p_id in ids_to_delete:
            product = session.get(Product, p_id)
            if product:
                print(f"Suppression de {product.name} (ID: {product.id})")
                session.delete(product)
            else:
                print(f"Produit avec ID {p_id} introuvable.")
        
        session.commit()
        print("Nettoyage terminé.")

if __name__ == "__main__":
    clean_catalog()
