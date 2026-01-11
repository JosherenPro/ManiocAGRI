from enum import Enum
from typing import Optional
from sqlmodel import Field, SQLModel

class UserRole(str, Enum):
    ADMIN = "admin"
    LIVREUR = "livreur"
    PRODUCTEUR = "producteur"
    GESTIONNAIRE = "gestionnaire"
    AGENT = "agent"
    CLIENT = "client"

class UserBase(SQLModel):
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    role: UserRole = Field(default=UserRole.CLIENT)
    is_active: bool = Field(default=True)
    is_approved: bool = Field(default=False)
    last_name: Optional[str] = None
    first_name: Optional[str] = None
    phone: Optional[str] = None

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int

class UserUpdate(SQLModel):
    username: Optional[str] = None
    email: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    is_approved: Optional[bool] = None
    last_name: Optional[str] = None
    first_name: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None
