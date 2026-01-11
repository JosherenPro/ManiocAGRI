from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from core.db import get_session
from core.security import create_access_token, verify_password, get_password_hash
from core.config import settings
from models.user import User, UserCreate, UserRead

router = APIRouter()

@router.post("/login/access-token")
def login_access_token(
    session: Session = Depends(get_session), 
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, retrieve an access token for future requests
    """
    user = session.exec(select(User).where(User.username == form_data.username.strip())).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/signup", response_model=UserRead)
def create_user_signup(
    *,
    session: Session = Depends(get_session),
    user_in: UserCreate
) -> Any:
    """
    Create new user without the need to be logged in.
    """
    user = session.exec(select(User).where(User.username == user_in.username)).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )
    
    # Check if email exists
    user_email = session.exec(select(User).where(User.email == user_in.email)).first()
    if user_email:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )

    db_obj = User(
        username=user_in.username,
        email=user_in.email,
        role=user_in.role,
        last_name=user_in.last_name,
        first_name=user_in.first_name,
        phone=user_in.phone,
        hashed_password=get_password_hash(user_in.password),
        is_active=True,
        is_approved=user_in.role == "client"  # Auto-approve clients, others need admin approval
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj
