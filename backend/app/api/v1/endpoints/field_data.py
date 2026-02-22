from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from api import deps
from core.db import get_session
from models.user import User
from models.field_data import FieldData, FieldDataCreate, FieldDataRead, FieldDataUpdate

router = APIRouter()


@router.post("/", response_model=FieldDataRead)
def create_field_data(
    *,
    session: Session = Depends(get_session),
    field_in: FieldDataCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Create new field data. Only for agents or admins."""
    if current_user.role not in ["agent", "admin"]:
        raise HTTPException(status_code=403, detail="Accès refusé — agent requis")
    db_obj = FieldData(
        location=field_in.location,
        size_hectares=field_in.size_hectares,
        season=field_in.season,
        soil_type=field_in.soil_type,
        planting_date=field_in.planting_date,
        expected_harvest_kg=field_in.expected_harvest_kg,
        notes=field_in.notes,
        agent_id=current_user.id,
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


@router.get("/", response_model=List[FieldDataRead])
def read_field_data(
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve field data.
    - Admins/Gestionnaire: all.
    - Agents: own only.
    """
    statement = select(FieldData)
    if current_user.role == "agent":
        statement = statement.where(FieldData.agent_id == current_user.id)
    elif current_user.role not in ["admin", "gestionnaire"]:
        raise HTTPException(status_code=403, detail="Accès refusé")
    return session.exec(statement.offset(skip).limit(limit)).all()


@router.get("/{id}", response_model=FieldDataRead)
def read_field_data_by_id(
    *,
    session: Session = Depends(get_session),
    id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Get a single field data record."""
    fd = session.get(FieldData, id)
    if not fd:
        raise HTTPException(status_code=404, detail="Données terrain non trouvées")
    if current_user.role == "agent" and fd.agent_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès refusé")
    return fd


@router.patch("/{id}", response_model=FieldDataRead)
def update_field_data(
    *,
    session: Session = Depends(get_session),
    id: int,
    field_in: FieldDataUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Update field data. Agent (own) or admin."""
    from datetime import datetime
    fd = session.get(FieldData, id)
    if not fd:
        raise HTTPException(status_code=404, detail="Données terrain non trouvées")
    if current_user.role == "agent" and fd.agent_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès refusé")
    if current_user.role not in ["agent", "admin", "gestionnaire"]:
        raise HTTPException(status_code=403, detail="Accès refusé")
    for key, value in field_in.dict(exclude_unset=True).items():
        setattr(fd, key, value)
    fd.updated_at = datetime.utcnow()
    session.add(fd)
    session.commit()
    session.refresh(fd)
    return fd
