from sqlalchemy import text
from core.db import engine
from sqlmodel import Session

def add_column():
    with Session(engine) as session:
        try:
            print("Adding livreur_id column to order table...")
            # Note: "order" is a reserved word in SQL, often needs quotes. In Postgres it's usually public.order or "order".
            # The error message showed table name "order".
            session.exec(text('ALTER TABLE "order" ADD COLUMN livreur_id INTEGER REFERENCES "user"(id);'))
            session.commit()
            print("Column added successfully.")
        except Exception as e:
            print(f"Error adding column (maybe it exists?): {e}")

if __name__ == "__main__":
    add_column()
