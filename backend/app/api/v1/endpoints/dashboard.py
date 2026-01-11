from typing import Any
from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from api import deps
from core.db import get_session
from models.user import User
from models.product import Product
from models.order import Order, OrderStatus
from models.field_data import FieldData

router = APIRouter()

@router.get("/summary")
def get_summary(
    *,
    session: Session = Depends(get_session),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get dashboard summary statistics.
    """
    # Base summary statistics
    stats = {}
    
    if current_user.role == "admin":
        stats["total_users"] = session.exec(select(func.count(User.id))).one()
        stats["unapproved_users"] = session.exec(
            select(func.count(User.id)).where(User.is_approved == False)
        ).one()
        stats["total_products"] = session.exec(select(func.count(Product.id))).one()
        stats["total_orders"] = session.exec(select(func.count(Order.id))).one()
        stats["pending_orders"] = session.exec(
            select(func.count(Order.id)).where(Order.status == OrderStatus.PENDING)
        ).one()
    
    elif current_user.role == "producteur":
        stats["my_products"] = session.exec(
            select(func.count(Product.id)).where(Product.producer_id == current_user.id)
        ).one()
        # Orders for their products could be added here if product-order relation exists
    
    elif current_user.role == "agent":
        stats["my_field_data_count"] = session.exec(
            select(func.count(FieldData.id)).where(FieldData.agent_id == current_user.id)
        ).one()
        
    elif current_user.role == "client":
        stats["my_orders_count"] = session.exec(
            select(func.count(Order.id)).where(Order.client_id == current_user.id)
        ).one()

    return stats
