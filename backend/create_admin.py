import sys
import os
import argparse

# Ensure app package is importable (same approach as seed_db.py)
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "app"))

from sqlmodel import Session, select, create_engine, SQLModel
from core.db import engine
from core.security import get_password_hash
from models.user import User, UserRole
import sqlalchemy


def create_admin(username: str, password: str, email: str):
    try:
        with Session(engine) as session:
            existing = session.exec(
                select(User).where(User.username == username)
            ).first()
            if existing:
                print(f"Utilisateur '{username}' existe déjà (id={existing.id}).")
                return

            user = User(
                username=username,
                email=email,
                role=UserRole.ADMIN,
                hashed_password=get_password_hash(password),
                is_active=True,
                is_approved=True,
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            print(f"Admin créé: username='{username}', id={user.id} (via primary DB)")
            return
    except sqlalchemy.exc.OperationalError as e:
        print(
            "Impossible de se connecter à la base distante, basculement vers une base SQLite locale."
        )

    # Fallback local SQLite DB (in backend/)
    local_db_path = os.path.join(current_dir, "manioc_agri.db")
    local_db_url = f"sqlite:///{local_db_path}"
    local_engine = create_engine(local_db_url, echo=False)
    SQLModel.metadata.create_all(local_engine)

    with Session(local_engine) as session:
        existing = session.exec(select(User).where(User.username == username)).first()
        if existing:
            print(
                f"Utilisateur '{username}' existe déjà dans la DB locale (id={existing.id})."
            )
            return

        user = User(
            username=username,
            email=email,
            role=UserRole.ADMIN,
            hashed_password=get_password_hash(password),
            is_active=True,
            is_approved=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        print(f"Admin créé: username='{username}', id={user.id} (via SQLite local)")


def main():
    parser = argparse.ArgumentParser(
        description="Créer un utilisateur admin dans la DB ManiocAgri"
    )
    parser.add_argument(
        "--username", required=True, help="Nom d'utilisateur de l'admin"
    )
    parser.add_argument("--password", required=True, help="Mot de passe pour l'admin")
    parser.add_argument("--email", default=None, help="Email de l'admin (optionnel)")

    args = parser.parse_args()
    email = args.email or f"{args.username}@maniocagri.local"
    create_admin(args.username, args.password, email)


if __name__ == "__main__":
    main()
