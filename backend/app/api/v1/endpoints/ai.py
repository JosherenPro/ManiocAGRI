from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel
from core.db import get_session
from api import deps
from models.user import User
from models.order import Order
from models.product import Product
from core.ai_service import chat_with_ai, DemandPredictor

router = APIRouter()


class ChatRequest(BaseModel):
    prompt: str


def _get_db_context(session: Session) -> dict:
    """Récupère les données utiles de la BDD pour enrichir le contexte IA."""
    try:
        products = session.exec(select(Product)).all()
        product_list = [
            {
                "name": p.name,
                "price": p.price,
                "stock_quantity": p.stock_quantity,
                "description": p.description or "",
            }
            for p in products
            if (getattr(p, "is_active", True))
        ]
    except Exception:
        product_list = []

    try:
        # Dernières 50 commandes pour le contexte
        orders = session.exec(select(Order).limit(50)).all()
        recent_orders = [{"id": o.id, "status": o.status} for o in orders]
    except Exception:
        recent_orders = []

    return {"products": product_list, "recent_orders": recent_orders}


@router.post("/chat")
async def chat_endpoint(
    request: ChatRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Interagir avec l'assistant Cerebras AI (authentifié) avec données BDD."""
    try:
        db_context = _get_db_context(session)
        response = await chat_with_ai(request.prompt, db_context=db_context)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat-public")
async def chat_public_endpoint(
    request: ChatRequest,
    session: Session = Depends(get_session),
) -> Any:
    """
    Chat public avec l'assistant IA - accessible sans authentification.
    Enrichi avec les données produits de la BDD en temps réel.
    """
    try:
        db_context = _get_db_context(session)
        response = await chat_with_ai(request.prompt, db_context=db_context)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forecast")
def get_demand_forecast(
    *,
    session: Session = Depends(get_session),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Obtenir les prévisions de demande. Réservé Admin/Gestionnaire."""
    if current_user.role not in ["admin", "gestionnaire"]:
        raise HTTPException(status_code=403, detail="Accès refusé")

    orders = session.exec(select(Order)).all()
    order_data = [{"created_at": o.created_at, "total_price": o.total_price} for o in orders]

    predictor = DemandPredictor()
    forecast = predictor.predict(order_data)

    return {"forecast": forecast}
