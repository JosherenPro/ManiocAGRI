from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class CategoryBase(SQLModel):
    name: str = Field(index=True, unique=True)
    slug: str = Field(index=True, unique=True)
    description: Optional[str] = None
    image_url: Optional[str] = None
    parent_id: Optional[int] = Field(default=None, foreign_key="category.id")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Category(CategoryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class CategoryCreate(SQLModel):
    name: str
    slug: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: bool = True


class CategoryRead(CategoryBase):
    id: int


class CategoryUpdate(SQLModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: Optional[bool] = None
