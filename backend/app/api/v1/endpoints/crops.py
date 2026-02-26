from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from api import deps
from core.db import get_session
from models.user import User
from models.crop import Crop, CropCreate, CropRead, CropUpdate
from models.field import Field

router = APIRouter()

@router.post("", response_model=CropRead)
def create_crop(
    *,
    session: Session = Depends(get_session),
    crop_in: CropCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Register a crop on a field. User must own the field."""
    field = session.get(Field, crop_in.field_id)
    if not field:
        raise HTTPException(status_code=404, detail="Champ non trouvé")
    
    if current_user.role not in ["admin", "gestionnaire"] and field.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Vous n'êtes pas le propriétaire de ce champ")

    db_obj = Crop.from_orm(crop_in)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

@router.get("/by-field/{field_id}", response_model=List[CropRead])
def read_crops(
    *,
    session: Session = Depends(get_session),
    field_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """List crops for a specific field."""
    field = session.get(Field, field_id)
    if not field:
        raise HTTPException(status_code=404, detail="Champ non trouvé")
    
    if current_user.role not in ["admin", "gestionnaire"] and field.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès refusé")

    statement = select(Crop).where(Crop.field_id == field_id)
    return session.exec(statement).all()
