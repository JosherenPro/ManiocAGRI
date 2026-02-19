"""
Script pour lister et supprimer les produits en double dans la base.
Les doublons visés sont les produits ajoutés par seed_db.py qui ont des noms
similaires à ceux ajoutés par add_missing_products.py.

Doublons identifiés (garder le plus récent / plus informatif) :
  - "Gari"  →  remplacé par "Gari d'Or" (plus descriptif)
  - "Farine de Manioc Séché" et "Farine de Manioc Humide"
    → si "Farine de Manioc" (générique) est aussi présent, garder les 3 (ils sont distincts)

Stratégie : afficher tous les produits, puis supprimer par nom ceux qui font doublon.
"""
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "app"))

from sqlmodel import Session, select
from core.db import engine
from models.product import Product

# Noms à SUPPRIMER (doublons / remplacés par un produit équivalent)
NAMES_TO_DELETE = [
    "Gari",   # remplacé par "Gari d'Or" (plus clair et cohérent avec l'accueil)
]


def list_all_products(session: Session):
    products = session.exec(select(Product).order_by(Product.id)).all()
    print(f"\n{'='*65}")
    print(f"  LISTE COMPLÈTE DES PRODUITS EN BASE ({len(products)} produits)")
    print(f"{'='*65}")
    for p in products:
        print(f"  id={p.id:3d} | {p.name:<38} | {p.price:>6} FCFA | stock={p.stock_quantity}")
    print(f"{'='*65}\n")
    return products


def remove_duplicates(session: Session):
    deleted = 0
    for name in NAMES_TO_DELETE:
        product = session.exec(select(Product).where(Product.name == name)).first()
        if product:
            session.delete(product)
            print(f"  [SUPPRIMÉ] '{name}' (id={product.id})")
            deleted += 1
        else:
            print(f"  [SKIP]     '{name}' introuvable en base")
    session.commit()
    return deleted


def main():
    with Session(engine) as session:
        print("\n--- État AVANT nettoyage ---")
        list_all_products(session)

        print("--- Suppression des doublons ---")
        deleted = remove_duplicates(session)

        print(f"\n--- État APRÈS nettoyage ---")
        list_all_products(session)

        print(f"✅ Nettoyage terminé : {deleted} produit(s) supprimé(s).")


if __name__ == "__main__":
    main()
