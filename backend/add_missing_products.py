"""
Script pour ajouter dans la base les produits présents sur la page d'accueil
mais absents du catalogue (base de données).

Produits existants dans seed_db.py :
  - Farine de Manioc Séché
  - Farine de Manioc Humide
  - Gari
  - Tapioca
  - Attiéké

Produits sur index.html NON présents en base :
  - Manioc Frais
  - Gari d'Or  (renommer Gari → Gari d'Or pour cohérence)
  - Gari Pur
  - Tubercule de Manioc
  - Manioc Premium
  - Farine de Manioc   (version générique, sans Séché/Humide)
"""
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "app"))

from sqlmodel import Session, select
from core.db import engine
from models.product import Product
from models.user import User, UserRole

MISSING_PRODUCTS = [
    {
        "name": "Manioc Frais",
        "description": "Manioc de qualité supérieure cultivé localement à la ferme MOKPOKPO.",
        "price": 350,
        "stock_quantity": 150,
        "image_url": "images/products/manioc2.jpg",
    },
    {
        "name": "Gari d'Or",
        "description": "Le trésor d'Afrique de l'Ouest, préparé selon la tradition ancestrale.",
        "price": 600,
        "stock_quantity": 200,
        "image_url": "images/products/gari.jpg",
    },
    {
        "name": "Gari Pur",
        "description": "Gari extra fin pour vos recettes raffinées. Sans additif.",
        "price": 650,
        "stock_quantity": 120,
        "image_url": "images/garipur.jpeg",
    },
    {
        "name": "Tubercule de Manioc",
        "description": "Tubercules fraîchement récoltés du champ, livrés dans les 24h.",
        "price": 300,
        "stock_quantity": 300,
        "image_url": "images/tubercule_manioc.jpg",
    },
    {
        "name": "Manioc Premium",
        "description": "Sélection premium de manioc cultivé biologiquement, certifié qualité MOKPOKPO.",
        "price": 500,
        "stock_quantity": 80,
        "image_url": "images/manic1.jpg",
    },
    {
        "name": "Farine de Manioc",
        "description": "Farine finement moulue, idéale pour la pâtisserie et la cuisine quotidienne.",
        "price": 550,
        "stock_quantity": 100,
        "image_url": "images/farine_manioc.webp",
    },
]


def get_producer(session: Session) -> User:
    """Retourne le premier producteur trouvé en base."""
    producer = session.exec(
        select(User).where(User.role == UserRole.PRODUCTEUR)
    ).first()
    if not producer:
        raise RuntimeError("Aucun producteur trouvé en base. Lancez seed_db.py d'abord.")
    return producer


def add_missing_products():
    with Session(engine) as session:
        producer = get_producer(session)
        print(f"Producteur utilisé : {producer.username} (id={producer.id})")

        added = 0
        skipped = 0
        for data in MISSING_PRODUCTS:
            existing = session.exec(
                select(Product).where(Product.name == data["name"])
            ).first()
            if existing:
                print(f"  [SKIP]  '{data['name']}' existe déjà (id={existing.id})")
                skipped += 1
                continue

            product = Product(
                name=data["name"],
                description=data["description"],
                price=data["price"],
                stock_quantity=data["stock_quantity"],
                image_url=data["image_url"],
                producer_id=producer.id,
            )
            session.add(product)
            print(f"  [ADD]   '{data['name']}' → {data['price']} FCFA, stock={data['stock_quantity']}")
            added += 1

        session.commit()
        print(f"\n✅ Terminé : {added} produit(s) ajouté(s), {skipped} ignoré(s) (déjà présents).")


if __name__ == "__main__":
    add_missing_products()
