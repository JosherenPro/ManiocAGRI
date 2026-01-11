from datetime import date, datetime
from typing import Optional
from sqlmodel import Field, SQLModel

class FieldDataBase(SQLModel):
    location: str
    size_hectares: float
    season: str
    soil_type: str
    planting_date: date
    expected_harvest_kg: int
    agent_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class FieldData(FieldDataBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class FieldDataCreate(FieldDataBase):
    pass

class FieldDataRead(FieldDataBase):
    id: int
