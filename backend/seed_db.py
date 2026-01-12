import sys
import os
from sqlmodel import Session, create_engine, select
from datetime import datetime, date, timedelta

# Ajouter le dossier parent au path pour les imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "app"))

from core.db import engine
from core.security import get_password_hash
from models.user import User, UserRole
from models.product import Product
from models.order import Order, OrderItem, OrderStatus
from models.field_data import FieldData

def seed_db():
    print("Démarrage du peuplement de la base de données...")
    with Session(engine) as session:
        # 1. Créer les Utilisateurs
        users_data = [
            ("admin", "admin@maniocagri.com", UserRole.ADMIN, True),
            ("producteur1", "p1@maniocagri.com", UserRole.PRODUCTEUR, True),
            ("agent1", "a1@maniocagri.com", UserRole.AGENT, True),
            ("livreur1", "l1@maniocagri.com", UserRole.LIVREUR, True),
            ("client1", "c1@maniocagri.com", UserRole.CLIENT, True),
            ("client2", "c2@maniocagri.com", UserRole.CLIENT, True),
            ("gestionnaire1", "g1@maniocagri.com", UserRole.GESTIONNAIRE, True),
        ]
        
        db_users = {}
        for username, email, role, approved in users_data:
            existing = session.exec(select(User).where(User.username == username)).first()
            if not existing:
                u = User(
                    username=username, 
                    email=email, 
                    role=role, 
                    hashed_password=get_password_hash("pass"), 
                    is_approved=approved,
                    is_active=True
                )
                session.add(u)
                session.commit()
                session.refresh(u)
                db_users[username] = u
                print(f"Utilisateur créé: {username}")
            else:
                db_users[username] = existing
        
        # 2. Créer les Produits
        prod1 = db_users["producteur1"]
        products_data = [
            ("Farine de Manioc Séché", "Qualité supérieure, parfaite pour le fufu.", 500, 100, "images/products/farine_manic_séché.jpeg"),
            ("Farine de Manioc Humide", "Idéal pour les préparations traditionnelles.", 450, 50, "images/products/farine_manioc_humide.jpeg"),
            ("Gari", "Gari croustillant et bien fermenté.", 600, 200, "images/products/gari.jpg"),
            ("Tapioca", "Grains fins de tapioca pour vos desserts.", 800, 30, "images/products/tapioca.jpeg"),
            ("Attiéké", "Attiéké frais prêt à consommer.", 700, 40, "images/products/atieke.jpg"),
        ]
        
        db_products = []
        for name, desc, price, qty, img in products_data:
            existing = session.exec(select(Product).where(Product.name == name)).first()
            if not existing:
                p = Product(name=name, description=desc, price=price, stock_quantity=qty, image_url=img, producer_id=prod1.id)
                session.add(p)
                print(f"Produit créé: {name}")
            else:
                p = existing
                p.image_url = img
                session.add(p)
            db_products.append(p)
        
        session.commit()
        for p in db_products:
            session.refresh(p)
            
        # 3. Créer des Commandes
        client1 = db_users["client1"]
        if not session.exec(select(Order).where(Order.client_name == "Client Test")).first():
            order1 = Order(
                order_number="CMD-DEMO-001",
                client_name="Client Test",
                phone="+228 90909090",
                delivery_address="Quartier Administratif, Lomé",
                status=OrderStatus.PENDING,
                total_price=2500,
                client_id=client1.id
            )
            session.add(order1)
            session.commit()
            session.refresh(order1)
            
            item1 = OrderItem(order_id=order1.id, product_id=db_products[0].id, quantity=5, unit_price=500)
            session.add(item1)
            print(f"Commande créée: {order1.order_number}")
            
        # 4. Créer des données de terrain
        agent1 = db_users["agent1"]
        if not session.exec(select(FieldData).where(FieldData.location == "Champ Nord")).first():
            field1 = FieldData(
                location="Champ Nord",
                size_hectares=2.5,
                season="Saison des pluies 2025",
                soil_type="Argileux-Sableux",
                planting_date=date.today() - timedelta(days=60),
                expected_harvest_kg=5000,
                agent_id=agent1.id
            )
            session.add(field1)
            print(f"Donnée terrain créée: {field1.location}")
            
        session.commit()
        print("Base de données peuplée avec succès !")

if __name__ == "__main__":
    seed_db()
