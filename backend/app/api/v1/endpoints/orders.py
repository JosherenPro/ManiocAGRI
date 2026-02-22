from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from api import deps
from core.db import get_session
from models.user import User
from models.order import (
    Order, OrderCreate, OrderRead, OrderUpdate, OrderItem,
    OrderStatus, OrderStatusUpdate, PaymentMethod
)

router = APIRouter()


@router.post("/", response_model=OrderRead)
def create_order(
    *,
    session: Session = Depends(get_session),
    order_in: OrderCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Create new order."""
    from datetime import datetime
    db_order = Order(
        order_number=order_in.order_number,
        client_name=order_in.client_name,
        phone=order_in.phone,
        delivery_address=order_in.delivery_address,
        total_price=order_in.total_price,
        discount=order_in.discount,
        delivery_zone_id=order_in.delivery_zone_id,
        client_id=current_user.id,
        status=OrderStatus.PENDING,
    )
    session.add(db_order)
    session.commit()
    session.refresh(db_order)

    from models.product import Product
    for item in order_in.items:
        product = session.get(Product, item.product_id)
        product_name = product.name if product else "Produit"
        db_item = OrderItem(
            order_id=db_order.id,
            product_id=item.product_id,
            product_name=product_name,
            quantity=item.quantity,
            unit_price=item.unit_price,
        )
        session.add(db_item)

    session.commit()
    session.refresh(db_order)
    return db_order


@router.get("/track/{number}", response_model=OrderRead)
def track_order(
    *,
    session: Session = Depends(get_session),
    number: str,
) -> Any:
    """Track an order by its number — public."""
    order = session.exec(select(Order).where(Order.order_number == number)).first()
    if not order:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    return order


@router.get("/", response_model=List[OrderRead])
def read_orders(
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    status: Optional[OrderStatus] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve orders with optional filters.
    - Admins/Gestionnaire: all orders.
    - Livreur: assigned orders.
    - Client: own orders.
    """
    from datetime import datetime
    statement = select(Order)

    if current_user.role == "client":
        statement = statement.where(Order.client_id == current_user.id)
    elif current_user.role == "livreur":
        statement = statement.where(Order.livreur_id == current_user.id)

    if status:
        statement = statement.where(Order.status == status)

    if date_from:
        try:
            dt_from = datetime.fromisoformat(date_from)
            statement = statement.where(Order.created_at >= dt_from)
        except ValueError:
            raise HTTPException(status_code=400, detail="Format date_from invalide (YYYY-MM-DD)")

    if date_to:
        try:
            dt_to = datetime.fromisoformat(date_to)
            statement = statement.where(Order.created_at <= dt_to)
        except ValueError:
            raise HTTPException(status_code=400, detail="Format date_to invalide (YYYY-MM-DD)")

    statement = statement.order_by(Order.created_at.desc())
    orders = session.exec(statement.offset(skip).limit(limit)).all()
    return orders


@router.get("/pending", response_model=List[OrderRead])
def read_pending_orders(
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_admin_or_gestionnaire),
) -> Any:
    """Get pending/validated orders without a livreur. Admin/Gestionnaire only."""
    statement = select(Order).where(
        (Order.status == OrderStatus.PENDING) |
        (Order.status == OrderStatus.VALIDATED)
    ).where(Order.livreur_id == None)
    orders = session.exec(statement.offset(skip).limit(limit)).all()
    return orders


@router.get("/{id}", response_model=OrderRead)
def read_order(
    *,
    session: Session = Depends(get_session),
    id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Get a single order by ID."""
    order = session.get(Order, id)
    if not order:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    # Authorization
    if current_user.role == "client" and order.client_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès refusé")
    if current_user.role == "livreur" and order.livreur_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès refusé")
    return order


@router.patch("/{id}/status", response_model=OrderRead)
def update_order_status(
    *,
    session: Session = Depends(get_session),
    id: int,
    order_update: OrderStatusUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Update order status. Staff only."""
    from datetime import datetime
    if current_user.role not in ["admin", "gestionnaire", "livreur"]:
        raise HTTPException(status_code=403, detail="Permissions insuffisantes")

    order = session.get(Order, id)
    if not order:
        raise HTTPException(status_code=404, detail="Commande non trouvée")

    if current_user.role == "livreur" and order.livreur_id != current_user.id:
        raise HTTPException(status_code=403, detail="Vous ne pouvez modifier que vos commandes assignées")

    order.status = order_update.status
    order.updated_at = datetime.utcnow()
    if order_update.notes:
        order.delivery_notes = order_update.notes

    session.add(order)
    session.commit()
    session.refresh(order)
    return order


@router.patch("/{id}/assign", response_model=OrderRead)
def assign_order_to_livreur(
    *,
    session: Session = Depends(get_session),
    id: int,
    livreur_id: int,
    current_user: User = Depends(deps.get_current_admin_or_gestionnaire),
) -> Any:
    """Assign an order to a livreur. Admin/Gestionnaire only."""
    from datetime import datetime
    order = session.get(Order, id)
    if not order:
        raise HTTPException(status_code=404, detail="Commande non trouvée")

    livreur = session.get(User, livreur_id)
    if not livreur:
        raise HTTPException(status_code=404, detail="Livreur non trouvé")
    if livreur.role != "livreur":
        raise HTTPException(status_code=400, detail="L'utilisateur spécifié n'est pas un livreur")
    if not livreur.is_approved:
        raise HTTPException(status_code=400, detail="Ce livreur n'est pas encore approuvé")

    order.livreur_id = livreur_id
    order.updated_at = datetime.utcnow()
    if order.status == OrderStatus.PENDING:
        order.status = OrderStatus.VALIDATED

    session.add(order)
    session.commit()
    session.refresh(order)
    return order


@router.patch("/{id}/payment", response_model=OrderRead)
def update_payment_status(
    *,
    session: Session = Depends(get_session),
    id: int,
    paid: bool,
    payment_method: Optional[PaymentMethod] = None,
    current_user: User = Depends(deps.get_current_admin_or_gestionnaire),
) -> Any:
    """Mark an order as paid. Admin/Gestionnaire only."""
    from datetime import datetime
    order = session.get(Order, id)
    if not order:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    order.paid = paid
    order.updated_at = datetime.utcnow()
    if payment_method is not None:
        order.payment_method = payment_method
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


@router.get("/livreurs/available", response_model=List[dict])
def get_available_livreurs(
    session: Session = Depends(get_session),
    current_user: User = Depends(deps.get_current_admin_or_gestionnaire),
) -> Any:
    """Get approved livreurs for assignment. Admin/Gestionnaire only."""
    livreurs = session.exec(
        select(User).where(User.role == "livreur").where(User.is_approved == True)
    ).all()
    return [{"id": l.id, "username": l.username, "email": l.email, "phone": l.phone} for l in livreurs]
