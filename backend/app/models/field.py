from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from models.crop import Crop

class FieldBase(SQLModel):
    name: str = Field(index=True)
    location_name: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    area_size_hectares: float

class Field(FieldBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    crops: List["Crop"] = Relationship(back_populates="field")

class FieldCreate(FieldBase):
    pass

class FieldRead(FieldBase):
    id: int
    owner_id: int
    created_at: datetime

class FieldUpdate(SQLModel):
    name: Optional[str] = None
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    area_size_hectares: Optional[float] = None
