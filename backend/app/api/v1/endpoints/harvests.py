from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from api import deps
from core.db import get_session
from models.user import User
from models.harvest import Harvest, HarvestCreate, HarvestRead, HarvestUpdate

router = APIRouter()


@router.get("/", response_model=List[HarvestRead])
def read_harvests(
    session: Session = Depends(get_session),
    current_user: User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    List harvests.
    - Agents: only their own.
    - Admin/Gestionnaire: all.
    """
    if current_user.role not in ["agent", "admin", "gestionnaire"]:
        raise HTTPException(status_code=403, detail="Accès refusé")

    statement = select(Harvest)
    if current_user.role == "agent":
        statement = statement.where(Harvest.agent_id == current_user.id)
    return session.exec(statement.offset(skip).limit(limit)).all()


@router.post("/", response_model=HarvestRead)
def create_harvest(
    *,
    session: Session = Depends(get_session),
    harvest_in: HarvestCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Record a harvest. Agents and admins only."""
    if current_user.role not in ["agent", "admin"]:
        raise HTTPException(status_code=403, detail="Accès refusé — agent requis")

    db_harvest = Harvest(
        field_data_id=harvest_in.field_data_id,
        agent_id=current_user.id,
        harvest_date=harvest_in.harvest_date,
        actual_kg=harvest_in.actual_kg,
        notes=harvest_in.notes,
    )
    session.add(db_harvest)
    session.commit()
    session.refresh(db_harvest)
    return db_harvest


@router.patch("/{id}", response_model=HarvestRead)
def update_harvest(
    *,
    session: Session = Depends(get_session),
    id: int,
    harvest_in: HarvestUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Update a harvest. Agent (own only) or admin."""
    harvest = session.get(Harvest, id)
    if not harvest:
        raise HTTPException(status_code=404, detail="Récolte non trouvée")
    if current_user.role == "agent" and harvest.agent_id != current_user.id:
        raise HTTPException(status_code=403, detail="Vous ne pouvez modifier que vos propres récoltes")
    if current_user.role not in ["agent", "admin", "gestionnaire"]:
        raise HTTPException(status_code=403, detail="Accès refusé")

    for key, value in harvest_in.dict(exclude_unset=True).items():
        setattr(harvest, key, value)
    session.add(harvest)
    session.commit()
    session.refresh(harvest)
    return harvest


@router.delete("/{id}")
def delete_harvest(
    *,
    session: Session = Depends(get_session),
    id: int,
    current_user: User = Depends(deps.get_current_active_admin),  # noqa: admin only

) -> Any:
    """Delete a harvest. Admin only."""
    harvest = session.get(Harvest, id)
    if not harvest:
        raise HTTPException(status_code=404, detail="Récolte non trouvée")
    session.delete(harvest)
    session.commit()
    return {"deleted": True}
