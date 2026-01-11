from sqlmodel import Session, select
from core.db import engine
from models.user import User, UserRole
from core.security import get_password_hash

def init_test_data():
    with Session(engine) as session:
        # 1. Admin
        admin = session.exec(select(User).where(User.username == "admin")).first()
        if not admin:
            print("Creating admin user...")
            admin = User(
                username="admin",
                email="admin@maniocagri.com",
                hashed_password=get_password_hash("pass"),
                role=UserRole.ADMIN,
                is_active=True,
                is_approved=True
            )
            session.add(admin)
        else:
            print("Resetting admin password...")
            admin.hashed_password = get_password_hash("pass")
            session.add(admin)
        
        # 2. Gestionnaire
        gest = session.exec(select(User).where(User.username == "gestionnaire1")).first()
        if not gest:
            print("Creating gestionnaire1...")
            gest = User(
                username="gestionnaire1",
                email="g1@maniocagri.com",
                hashed_password=get_password_hash("pass"),
                role=UserRole.GESTIONNAIRE,
                is_active=True,
                is_approved=True
            )
            session.add(gest)
        else:
            print("Resetting gestionnaire1 password...")
            gest.hashed_password = get_password_hash("pass")
            session.add(gest)

        # 3. Producteur
        prod = session.exec(select(User).where(User.username == "producteur1")).first()
        if not prod:
            print("Creating producteur1...")
            prod = User(
                username="producteur1",
                email="p1@maniocagri.com",
                hashed_password=get_password_hash("pass"),
                role=UserRole.PRODUCTEUR,
                is_active=True,
                is_approved=True
            )
            session.add(prod)
        else:
            print("Resetting producteur1 password...")
            prod.hashed_password = get_password_hash("pass")
            session.add(prod)

        # 4. Client
        client = session.exec(select(User).where(User.username == "client1")).first()
        if not client:
            print("Creating client1...")
            client = User(
                username="client1",
                email="c1@maniocagri.com",
                hashed_password=get_password_hash("pass"),
                role=UserRole.CLIENT,
                is_active=True,
                is_approved=True
            )
            session.add(client)
        else:
            print("Resetting client1 password...")
            client.hashed_password = get_password_hash("pass")
            session.add(client)

        session.commit()
        print("Test data initialized successfully!")

if __name__ == "__main__":
    init_test_data()
