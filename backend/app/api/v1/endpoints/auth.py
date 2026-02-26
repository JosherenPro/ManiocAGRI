from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select, SQLModel
from core.db import get_session
import logging

from core.security import create_access_token, verify_password, get_password_hash
from core.config import settings
from models.user import User, UserCreate, UserRead, UserRole
from google.oauth2 import id_token
from google.auth.transport import requests
import secrets

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/login/access-token")
def login_access_token(
    session: Session = Depends(get_session),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, retrieve an access token for future requests
    """
    user = session.exec(
        select(User).where(User.username == form_data.username.strip())
    ).first()
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
    *, session: Session = Depends(get_session), user_in: UserCreate
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
        is_approved=user_in.role
        == "client",  # Auto-approve clients, others need admin approval
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


class GoogleAuthRequest(SQLModel):
    token: str
    requested_role: str = "client"


@router.post("/google")
def google_auth(
    request: GoogleAuthRequest, session: Session = Depends(get_session)
) -> Any:
    """
    Verify Google token and login/register the user
    """
    # Guard: ensure GOOGLE_CLIENT_ID is configured
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=500, detail="GOOGLE_CLIENT_ID not configured on server"
        )

    try:
        # Validate the token with Google
        # clock_skew allows for a small difference in time between the server and Google's servers
        idinfo = id_token.verify_oauth2_token(
            request.token, requests.Request(), settings.GOOGLE_CLIENT_ID, clock_skew=10
        )

        email = idinfo.get("email")
        first_name = idinfo.get("given_name", "")
        last_name = idinfo.get("family_name", "")

        if not email:
            raise HTTPException(status_code=400, detail="Email not provided by Google")

        # Check if user exists
        user = session.exec(select(User).where(User.email == email)).first()

        if not user:
            # Generate a random password since they login with Google
            random_password = secrets.token_urlsafe(32)

            # The username from email prefix (and ensure it's unique if needed)
            base_username = email.split("@")[0]
            username = base_username
            counter = 1
            while session.exec(select(User).where(User.username == username)).first():
                username = f"{base_username}{counter}"
                counter += 1

            # Determine role and approval
            role = UserRole.CLIENT
            is_approved = True

            # Auto-admin for the specified email
            if email == "josherenprofessional@gmail.com":
                role = UserRole.ADMIN
                is_approved = True
            else:
                try:
                    role = UserRole(request.requested_role)
                except ValueError:
                    role = UserRole.CLIENT

                # Only clients are auto-approved. Others need admin validation.
                if role != UserRole.CLIENT:
                    is_approved = False

            user = User(
                username=username,
                email=email,
                role=role,
                last_name=last_name,
                first_name=first_name,
                hashed_password=get_password_hash(random_password),
                is_active=True,
                is_approved=is_approved,
            )
            session.add(user)
            session.commit()
            session.refresh(user)

        elif not user.is_active:
            raise HTTPException(status_code=400, detail="Compte inactif")

        elif not user.is_approved:
            raise HTTPException(
                status_code=400, detail="Compte en attente d'approbation"
            )

        # Generate standard access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return {
            "access_token": create_access_token(
                user.id, expires_delta=access_token_expires
            ),
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "role": user.role,
            },
        }

    except ValueError as e:
        # Invalid token
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error in google_auth")
        raise HTTPException(status_code=500, detail="Internal authentication error")
