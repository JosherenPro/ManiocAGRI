from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from api import deps
from models.user import User
from models.field import Field
from sqlmodel import Session
from core.db import get_session
from services.weather_service import weather_service

router = APIRouter()

@router.get("/{field_id}")
async def get_field_weather(
    *,
    session: Session = Depends(get_session),
    field_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Get current weather for a specific field."""
    field = session.get(Field, field_id)
    if not field:
        raise HTTPException(status_code=404, detail="Champ non trouvé")
    
    # Check permission (owner or admin/gestionnaire)
    if current_user.role not in ["admin", "gestionnaire"] and field.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès refusé")

    # Use location_name for weather lookup
    weather_data = await weather_service.get_weather(field.location_name)
    return weather_data
