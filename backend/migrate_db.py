from app.core.db import engine
from sqlalchemy import text
import sys

def migrate():
    try:
        with engine.connect() as conn:
            # Check if columns exist
            res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='order'"))
            columns = [row[0] for row in res]
            print(f"Current columns in 'order' table: {columns}")
            
            if 'delivery_notes' not in columns:
                print("Adding 'delivery_notes' column...")
                conn.execute(text("ALTER TABLE \"order\" ADD COLUMN delivery_notes VARCHAR"))
                conn.commit()
                print("Column 'delivery_notes' added successfully.")
            else:
                print("Column 'delivery_notes' already exists.")
    except Exception as e:
        print(f"Error during migration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    migrate()
