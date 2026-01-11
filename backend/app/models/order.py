from datetime import datetime
from enum import Enum
from typing import List, Optional
from sqlmodel import Field, SQLModel, Relationship

class OrderStatus(str, Enum):
    PENDING = "En attente de validation"
    VALIDATED = "Validée - En préparation"
    IN_TRANSIT = "En transit"
    DELIVERED = "Livré"
    REJECTED = "Refusée"

class OrderItemBase(SQLModel):
    product_id: int = Field(foreign_key="product.id")
    quantity: int
    unit_price: int

class OrderItem(OrderItemBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    order: "Order" = Relationship(back_populates="items")

class OrderBase(SQLModel):
    order_number: str = Field(index=True, unique=True)
    client_name: str
    phone: str
    delivery_address: str
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    total_price: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    client_id: Optional[int] = Field(default=None, foreign_key="user.id")
    livreur_id: Optional[int] = Field(default=None, foreign_key="user.id")

class Order(OrderBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    items: List["OrderItem"] = Relationship(back_populates="order")

class OrderCreate(OrderBase):
    items: List[OrderItemBase]

class OrderRead(OrderBase):
    id: int
    items: List[OrderItemBase]

class OrderUpdate(SQLModel):
    status: Optional[OrderStatus] = None
    delivery_address: Optional[str] = None
