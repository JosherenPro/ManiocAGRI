from sqlmodel import create_engine, text
from core.config import settings

def migrate():
    print(f"Connecting to database...")
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        try:
            print("Adding last_name...")
            conn.execute(text("ALTER TABLE \"user\" ADD COLUMN last_name VARCHAR"))
            print("Adding first_name...")
            conn.execute(text("ALTER TABLE \"user\" ADD COLUMN first_name VARCHAR"))
            print("Adding phone...")
            conn.execute(text("ALTER TABLE \"user\" ADD COLUMN phone VARCHAR"))
            conn.commit()
            print("Columns added successfully")
        except Exception as e:
            print(f"Migration failed (maybe columns exist?): {e}")

if __name__ == "__main__":
    migrate()
