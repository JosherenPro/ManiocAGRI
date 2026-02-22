from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from api import deps
from core.db import get_session
from models.user import User
from models.delivery_zone import DeliveryZone, DeliveryZoneCreate, DeliveryZoneRead, DeliveryZoneUpdate

router = APIRouter()


@router.get("/", response_model=List[DeliveryZoneRead])
def read_delivery_zones(session: Session = Depends(get_session)) -> Any:
    """List all active delivery zones — public."""
    zones = session.exec(
        select(DeliveryZone).where(DeliveryZone.is_active == True)
    ).all()
    return zones


@router.get("/all", response_model=List[DeliveryZoneRead])
def read_all_delivery_zones(
    session: Session = Depends(get_session),
    current_user: User = Depends(deps.get_current_admin_or_gestionnaire),
) -> Any:
    """List all delivery zones including inactive ones. Admin/Gestionnaire only."""
    return session.exec(select(DeliveryZone)).all()


@router.post("/", response_model=DeliveryZoneRead)
def create_delivery_zone(
    *,
    session: Session = Depends(get_session),
    zone_in: DeliveryZoneCreate,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """Create a new delivery zone. Admin only."""
    existing = session.exec(
        select(DeliveryZone).where(DeliveryZone.name == zone_in.name)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Une zone avec ce nom existe déjà")
    db_zone = DeliveryZone.from_orm(zone_in)
    session.add(db_zone)
    session.commit()
    session.refresh(db_zone)
    return db_zone


@router.patch("/{id}", response_model=DeliveryZoneRead)
def update_delivery_zone(
    *,
    session: Session = Depends(get_session),
    id: int,
    zone_in: DeliveryZoneUpdate,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """Update a delivery zone. Admin only."""
    zone = session.get(DeliveryZone, id)
    if not zone:
        raise HTTPException(status_code=404, detail="Zone non trouvée")
    for key, value in zone_in.dict(exclude_unset=True).items():
        setattr(zone, key, value)
    session.add(zone)
    session.commit()
    session.refresh(zone)
    return zone


@router.delete("/{id}", response_model=DeliveryZoneRead)
def delete_delivery_zone(
    *,
    session: Session = Depends(get_session),
    id: int,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """Delete a delivery zone. Admin only."""
    zone = session.get(DeliveryZone, id)
    if not zone:
        raise HTTPException(status_code=404, detail="Zone non trouvée")
    session.delete(zone)
    session.commit()
    return zone
