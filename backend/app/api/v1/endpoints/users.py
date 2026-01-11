from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from api import deps
from core.db import get_session
from core.security import get_password_hash
from models.user import User, UserRead, UserUpdate, UserCreate

router = APIRouter()

@router.get("/me", response_model=UserRead)
def read_user_me(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.get("/", response_model=List[UserRead])
def read_users(
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_admin_or_gestionnaire),
) -> Any:
    """
    Retrieve users. Admin et gestionnaire only.
    """
    users = session.exec(select(User).offset(skip).limit(limit)).all()
    return users

@router.post("/", response_model=UserRead)
def create_user(
    *,
    session: Session = Depends(get_session),
    user_in: UserCreate,
    current_user: User = Depends(deps.get_current_admin_or_gestionnaire),
) -> Any:
    """
    Create a new user. Admin et gestionnaire only.
    """
    # Check if user already exists
    existing_user = session.exec(
        select(User).where((User.username == user_in.username) | (User.email == user_in.email))
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=400, 
            detail="Un utilisateur avec ce nom ou email existe déjà"
        )
    
    # Create user
    db_user = User(
        username=user_in.username,
        email=user_in.email,
        role=user_in.role,
        last_name=user_in.last_name,
        first_name=user_in.first_name,
        phone=user_in.phone,
        is_active=user_in.is_active,
        is_approved=True,  # Admin/gestionnaire created users are auto-approved
        hashed_password=get_password_hash(user_in.password)
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    # Background tasks would be better for production
    try:
        import asyncio
        from core.email_service import send_welcome_email
        asyncio.create_task(send_welcome_email(db_user.email, db_user.username))
    except Exception as e:
        print(f"Error sending welcome email: {e}")

    return db_user

@router.patch("/{id}/approve", response_model=UserRead)
def approve_user(
    *,
    session: Session = Depends(get_session),
    id: int,
    current_user: User = Depends(deps.get_current_admin_or_gestionnaire),
) -> Any:
    """
    Approve a user registration. Admin et gestionnaire only.
    """
    user = session.get(User, id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    user.is_approved = True
    session.add(user)
    session.commit()
    session.refresh(user)

    # Send approval email
    try:
        import asyncio
        from core.email_service import send_approval_email
        asyncio.create_task(send_approval_email(user.email, user.username))
    except Exception as e:
        print(f"Error sending approval email: {e}")

    return user

@router.delete("/{id}", response_model=UserRead)
def delete_user(
    *,
    session: Session = Depends(get_session),
    id: int,
    current_user: User = Depends(deps.get_current_admin_or_gestionnaire),
) -> Any:
    """
    Delete a user. Admin et gestionnaire only.
    Cannot delete yourself or another admin.
    """
    user = session.get(User, id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Vous ne pouvez pas vous supprimer vous-même")
    
    if user.role == "admin" and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Seul un admin peut supprimer un autre admin")
    
    session.delete(user)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=400,
            detail="Impossible de supprimer cet utilisateur car il est lié à des commandes. Veuillez le désactiver à la place."
        )
    return user

@router.patch("/{id}", response_model=UserRead)
def update_user(
    *,
    session: Session = Depends(get_session),
    id: int,
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_admin_or_gestionnaire),
) -> Any:
    """
    Update a user. Admin et gestionnaire only.
    """
    user = session.get(User, id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    user_data = user_in.dict(exclude_unset=True)
    
    # If password is being updated, hash it
    if "password" in user_data and user_data["password"]:
        user_data["hashed_password"] = get_password_hash(user_data.pop("password"))
    elif "password" in user_data:
        del user_data["password"]
    
    for key, value in user_data.items():
        setattr(user, key, value)
    
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
