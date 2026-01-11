from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from api import deps
from core.db import get_session
from models.user import User
from models.field_data import FieldData, FieldDataCreate, FieldDataRead

router = APIRouter()

@router.post("/", response_model=FieldDataRead)
def create_field_data(
    *,
    session: Session = Depends(get_session),
    field_in: FieldDataCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Create new field data. Only for agents or admins.
    """
    if current_user.role not in ["agent", "admin"]:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    db_obj = FieldData.from_orm(field_in)
    db_obj.agent_id = current_user.id
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
    - Admins see all.
    - Agents see their own.
    """
    statement = select(FieldData)
    if current_user.role == "agent":
        statement = statement.where(FieldData.agent_id == current_user.id)
    elif current_user.role != "admin":
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    data = session.exec(statement.offset(skip).limit(limit)).all()
    return data
