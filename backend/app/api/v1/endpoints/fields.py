from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from api import deps
from core.db import get_session
from models.user import User
from models.field import Field, FieldCreate, FieldRead, FieldUpdate

router = APIRouter()

@router.post("", response_model=FieldRead)
def create_field(
    *,
    session: Session = Depends(get_session),
    field_in: FieldCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Create a new field. Producers, agents, or admins only."""
    if current_user.role not in ["producteur", "agent", "admin"]:
        raise HTTPException(status_code=403, detail="Permissions insuffisantes")
    
    db_obj = Field(**field_in.dict(), owner_id=current_user.id)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

@router.get("", response_model=List[FieldRead])
def read_fields(
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Retrieve fields. Users see only their own unless they are admin/gestionnaire."""
    statement = select(Field)
    if current_user.role not in ["admin", "gestionnaire"]:
        statement = statement.where(Field.owner_id == current_user.id)
    
    return session.exec(statement.offset(skip).limit(limit)).all()
