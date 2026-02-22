import logging
from typing import Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from api import deps
from core.db import get_session
from models.user import User
from models.product import Product
from models.order import Order, OrderStatus
from models.field_data import FieldData

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/summary")
def get_summary(
    *,
    session: Session = Depends(get_session),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Get role-specific dashboard statistics."""
    stats: dict = {}
    today = datetime.utcnow().date()

    # ── Admin ─────────────────────────────────────────────────────────────
    if current_user.role == "admin":
        stats["total_users"] = session.exec(select(func.count(User.id))).one()
        stats["unapproved_users"] = session.exec(
            select(func.count(User.id)).where(User.is_approved == False)
        ).one()
        stats["total_products"] = session.exec(select(func.count(Product.id))).one()
        stats["active_products"] = session.exec(
            select(func.count(Product.id)).where(Product.is_active == True)
        ).one()
        stats["total_orders"] = session.exec(select(func.count(Order.id))).one()
        stats["pending_orders"] = session.exec(
            select(func.count(Order.id)).where(Order.status == OrderStatus.PENDING)
        ).one()
        # Revenue (paid orders) 
        paid_total = session.exec(
            select(func.sum(Order.total_price)).where(Order.paid == True)
        ).one()
        stats["total_revenue_fcfa"] = paid_total or 0

    # ── Gestionnaire ──────────────────────────────────────────────────────
    elif current_user.role == "gestionnaire":
        stats["total_orders"] = session.exec(select(func.count(Order.id))).one()
        stats["pending_orders"] = session.exec(
            select(func.count(Order.id)).where(Order.status == OrderStatus.PENDING)
        ).one()
        stats["in_transit_orders"] = session.exec(
            select(func.count(Order.id)).where(Order.status == OrderStatus.IN_TRANSIT)
        ).one()
        stats["delivered_today"] = session.exec(
            select(func.count(Order.id))
            .where(Order.status == OrderStatus.DELIVERED)
            .where(func.date(Order.updated_at) == today)
        ).one()
        paid_today = session.exec(
            select(func.sum(Order.total_price))
            .where(Order.paid == True)
            .where(func.date(Order.created_at) == today)
        ).one()
        stats["revenue_today_fcfa"] = paid_today or 0
        stats["unassigned_orders"] = session.exec(
            select(func.count(Order.id)).where(Order.livreur_id == None)
            .where(Order.status != OrderStatus.DELIVERED)
            .where(Order.status != OrderStatus.REJECTED)
        ).one()

    # ── Livreur ───────────────────────────────────────────────────────────
    elif current_user.role == "livreur":
        stats["assigned_orders"] = session.exec(
            select(func.count(Order.id)).where(Order.livreur_id == current_user.id)
        ).one()
        stats["in_transit"] = session.exec(
            select(func.count(Order.id))
            .where(Order.livreur_id == current_user.id)
            .where(Order.status == OrderStatus.IN_TRANSIT)
        ).one()
        stats["delivered"] = session.exec(
            select(func.count(Order.id))
            .where(Order.livreur_id == current_user.id)
            .where(Order.status == OrderStatus.DELIVERED)
        ).one()

    # ── Producteur ────────────────────────────────────────────────────────
    elif current_user.role == "producteur":
        stats["my_products"] = session.exec(
            select(func.count(Product.id)).where(Product.producer_id == current_user.id)
        ).one()
        stats["active_products"] = session.exec(
            select(func.count(Product.id))
            .where(Product.producer_id == current_user.id)
            .where(Product.is_active == True)
        ).one()
        low_stock_items = session.exec(
            select(Product)
            .where(Product.producer_id == current_user.id)
            .where(Product.stock_quantity < 50)
        ).all()
        stats["low_stock_products"] = [
            {"id": p.id, "name": p.name, "stock": p.stock_quantity} for p in low_stock_items
        ]

    # ── Agent terrain ─────────────────────────────────────────────────────
    elif current_user.role == "agent":
        stats["my_field_data_count"] = session.exec(
            select(func.count(FieldData.id)).where(FieldData.agent_id == current_user.id)
        ).one()
        from models.harvest import Harvest
        stats["my_harvests_count"] = session.exec(
            select(func.count(Harvest.id)).where(Harvest.agent_id == current_user.id)
        ).one()

    # ── Client ────────────────────────────────────────────────────────────
    elif current_user.role == "client":
        stats["my_orders_count"] = session.exec(
            select(func.count(Order.id)).where(Order.client_id == current_user.id)
        ).one()
        stats["pending_orders"] = session.exec(
            select(func.count(Order.id))
            .where(Order.client_id == current_user.id)
            .where(Order.status == OrderStatus.PENDING)
        ).one()

    return stats
