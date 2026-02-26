from datetime import date, datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from models.field import Field

class CropStatus(str, Enum):
    PLANTED = "planted"    # Mis en terre
    GROWING = "growing"    # En croissance
    MATURE = "mature"      # Prêt pour récolte
    HARVESTED = "harvested" # Récolté
    FAILED = "failed"      # Échec / Abandonné

class CropBase(SQLModel):
    field_id: int = Field(foreign_key="field.id", index=True)
    crop_type: str  # ex: "Manioc", "Maïs"
    variety: Optional[str] = None
    area_occupied_hectares: float = Field(default=0.0) # Superficie occupée sur le champ
    planting_date: date
    expected_harvest_date: Optional[date] = None
    status: CropStatus = Field(default=CropStatus.PLANTED)

class Crop(CropBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    field: "Field" = Relationship(back_populates="crops")

class CropCreate(CropBase):
    pass

class CropRead(CropBase):
    id: int

class CropUpdate(SQLModel):
    crop_type: Optional[str] = None
    variety: Optional[str] = None
    area_occupied_hectares: Optional[float] = None
    planting_date: Optional[date] = None
    expected_harvest_date: Optional[date] = None
    status: Optional[CropStatus] = None
