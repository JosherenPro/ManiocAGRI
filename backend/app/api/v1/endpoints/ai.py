from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from core.db import get_session
from api import deps
from models.user import User
from models.order import Order
from core.ai_service import chat_with_ai, DemandPredictor

router = APIRouter()

from pydantic import BaseModel

class ChatRequest(BaseModel):
    prompt: str

@router.post("/chat")
async def chat_endpoint(
    request: ChatRequest,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Interagir avec l'assistant Cerebras AI (authentifié).
    """
    try:
        response = await chat_with_ai(request.prompt)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat-public")
async def chat_public_endpoint(
    request: ChatRequest,
) -> Any:
    """
    Chat public avec l'assistant IA - accessible sans authentification.
    Utilisé depuis la page d'accueil pour les visiteurs.
    """
    try:
        response = await chat_with_ai(request.prompt)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/forecast")
def get_demand_forecast(
    *,
    session: Session = Depends(get_session),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Obtenir les prévisions de demande. Réservé Admin/Gestionnaire.
    """
    if current_user.role not in ["admin", "gestionnaire"]:
        raise HTTPException(status_code=403, detail="Accès refusé")
        
    orders = session.exec(select(Order)).all()
    order_data = [{"created_at": o.created_at, "total_price": o.total_price} for o in orders]
    
    predictor = DemandPredictor()
    forecast = predictor.predict(order_data)
    
    return {"forecast": forecast}
