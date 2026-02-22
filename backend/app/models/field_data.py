from datetime import date, datetime
from enum import Enum
from typing import Optional
from sqlmodel import Field, SQLModel


class FieldDataStatus(str, Enum):
    ACTIVE = "active"
    HARVESTED = "harvested"
    ABANDONED = "abandoned"


class FieldDataBase(SQLModel):
    location: str
    size_hectares: float
    season: str
    soil_type: str
    planting_date: date
    expected_harvest_kg: int
    actual_harvest_kg: Optional[int] = Field(default=None)
    notes: Optional[str] = Field(default=None)
    status: FieldDataStatus = Field(default=FieldDataStatus.ACTIVE)
    agent_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)


class FieldData(FieldDataBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class FieldDataCreate(SQLModel):
    location: str
    size_hectares: float
    season: str
    soil_type: str
    planting_date: date
    expected_harvest_kg: int
    notes: Optional[str] = None


class FieldDataRead(FieldDataBase):
    id: int


class FieldDataUpdate(SQLModel):
    location: Optional[str] = None
    size_hectares: Optional[float] = None
    season: Optional[str] = None
    soil_type: Optional[str] = None
    planting_date: Optional[date] = None
    expected_harvest_kg: Optional[int] = None
    actual_harvest_kg: Optional[int] = None
    notes: Optional[str] = None
    status: Optional[FieldDataStatus] = None
