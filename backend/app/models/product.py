from typing import Optional
from sqlmodel import Field, SQLModel

class ProductBase(SQLModel):
    name: str = Field(index=True)
    description: Optional[str] = None
    price: int = Field(default=0)
    stock_quantity: int = Field(default=0)
    image_url: Optional[str] = None
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
