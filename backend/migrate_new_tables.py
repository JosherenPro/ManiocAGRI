"""
Migration script — crée toutes les nouvelles tables et colonnes.
Usage: python migrate_new_tables.py
"""
import sys
import os

# Add /app to path so models are importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))
os.chdir(os.path.join(os.path.dirname(__file__), "app"))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from sqlmodel import SQLModel
from core.db import engine

# Import ALL models so SQLModel registers them in metadata
from models.user import User
from models.product import Product
from models.order import Order, OrderItem
from models.field_data import FieldData
from models.category import Category
from models.notification import Notification
from models.delivery_zone import DeliveryZone
from models.review import ProductReview
from models.transaction import Transaction
from models.harvest import Harvest

if __name__ == "__main__":
    print("🌱 Creating / updating all tables...")
    SQLModel.metadata.create_all(engine)
    print("✅ Migration complete!")
    print("\nTables disponibles:")
    for table in sorted(SQLModel.metadata.tables.keys()):
        print(f"  • {table}")
