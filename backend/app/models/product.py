from typing import Optional
from sqlmodel import Field, SQLModel


class ProductBase(SQLModel):
    name: str = Field(index=True)
    description: Optional[str] = None
    price: int = Field(default=0)
    stock_quantity: int = Field(default=0)
    image_url: Optional[str] = None
    unit: str = Field(default="kg")  # kg, sachet, litre, tonne
    is_active: bool = Field(default=True)
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")
    producer_id: Optional[int] = Field(default=None, foreign_key="user.id")


class Product(ProductBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class ProductCreate(ProductBase):
    pass


class ProductRead(ProductBase):
    id: int


class ProductUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    stock_quantity: Optional[int] = None
    image_url: Optional[str] = None
    unit: Optional[str] = None
    is_active: Optional[bool] = None
    category_id: Optional[int] = None
