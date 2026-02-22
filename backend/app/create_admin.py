from sqlmodel import Session, select
from core.db import engine
from models.user import User, UserRole
from core.security import get_password_hash
import secrets

with Session(engine) as session:
    email = "josherenprofessional@gmail.com"
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        user = User(
            username="josheren_admin",
            email=email,
            role=UserRole.ADMIN,
            is_active=True,
            is_approved=True,
            hashed_password=get_password_hash(secrets.token_urlsafe(32))
        )
        session.add(user)
    else:
        user.role = UserRole.ADMIN
        user.is_approved = True
        session.add(user)
    session.commit()
    print("Admin user created/updated successfully.")
