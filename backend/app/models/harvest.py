from datetime import date, datetime
from enum import Enum
from typing import Optional
from sqlmodel import Field, SQLModel


class HarvestStatus(str, Enum):
    DECLARED = "declared"
    VERIFIED = "verified"
    PROCESSED = "processed"


class HarvestBase(SQLModel):
    field_data_id: int = Field(foreign_key="fielddata.id", index=True)
    agent_id: int = Field(foreign_key="user.id", index=True)
    harvest_date: date
    actual_kg: int  # actual harvest in kg
    notes: Optional[str] = None
    status: HarvestStatus = Field(default=HarvestStatus.DECLARED)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Harvest(HarvestBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class HarvestCreate(SQLModel):
    field_data_id: int
    harvest_date: date
    actual_kg: int
    notes: Optional[str] = None


class HarvestRead(HarvestBase):
    id: int


class HarvestUpdate(SQLModel):
    harvest_date: Optional[date] = None
    actual_kg: Optional[int] = None
    notes: Optional[str] = None
    status: Optional[HarvestStatus] = None
