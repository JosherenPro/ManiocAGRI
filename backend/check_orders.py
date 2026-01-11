import sys
import os
from sqlmodel import Session, select

# Ajouter le dossier parent au path pour les imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "app"))

from core.db import engine
from models.order import Order

def list_orders():
    print("Liste des commandes en base de données :")
    with Session(engine) as session:
        orders = session.exec(select(Order)).all()
        if not orders:
            print("Aucune commande trouvée.")
        for o in orders:
            print(f"ID: {o.id} | No: {o.order_number} | Client: {o.client_name} | Total: {o.total_price} | Status: {o.status}")

if __name__ == "__main__":
    list_orders()
