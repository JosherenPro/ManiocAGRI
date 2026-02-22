from typing import Optional
from sqlmodel import Field, SQLModel


class DeliveryZoneBase(SQLModel):
    name: str = Field(index=True, unique=True)
    description: Optional[str] = None
    delivery_fee: int = Field(default=0)  # FCFA
    estimated_days: int = Field(default=1)
    is_active: bool = Field(default=True)


class DeliveryZone(DeliveryZoneBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class DeliveryZoneCreate(SQLModel):
    name: str
    description: Optional[str] = None
    delivery_fee: int = 0
    estimated_days: int = 1
    is_active: bool = True


class DeliveryZoneRead(DeliveryZoneBase):
    id: int


class DeliveryZoneUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    delivery_fee: Optional[int] = None
    estimated_days: Optional[int] = None
    is_active: Optional[bool] = None
