from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from api import deps
from api.deps import get_current_admin_or_gestionnaire
from core.db import get_session
from models.user import User
from models.order import Order, OrderCreate, OrderRead, OrderUpdate, OrderItem, OrderStatus, OrderStatusUpdate

router = APIRouter()

@router.post("/", response_model=OrderRead)
def create_order(
    *,
    session: Session = Depends(get_session),
    order_in: OrderCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Create new order.
    """
    # Create the order
    db_order = Order(
        order_number=order_in.order_number,
        client_name=order_in.client_name,
        phone=order_in.phone,
        delivery_address=order_in.delivery_address,
        total_price=order_in.total_price,
        client_id=current_user.id,
        status=OrderStatus.PENDING
    )
    session.add(db_order)
    session.commit()
    session.refresh(db_order)
    
    # Create order items
    for item in order_in.items:
        db_item = OrderItem(
            order_id=db_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.unit_price
        )
        session.add(db_item)
    
    session.commit()
    session.refresh(db_order)
    return db_order

@router.get("/track/{number}", response_model=OrderRead)
def track_order(
    *,
    session: Session = Depends(get_session),
    number: str
) -> Any:
    """
    Track an order by its number.
    """
    order = session.exec(select(Order).where(Order.order_number == number)).first()
    if not order:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    return order

@router.get("/", response_model=List[OrderRead])
def read_orders(
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve orders.
    - Admins/Managers see all.
    - Drivers see assigned orders.
    - Clients see their own.
    """
    statement = select(Order)
    if current_user.role == "client":
        statement = statement.where(Order.client_id == current_user.id)
    elif current_user.role == "livreur":
        statement = statement.where(Order.livreur_id == current_user.id)
    
    orders = session.exec(statement.offset(skip).limit(limit)).all()
    return orders

@router.get("/pending", response_model=List[OrderRead])
def read_pending_orders(
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_admin_or_gestionnaire),
) -> Any:
    """
    Get all pending orders that need assignment. Admin/Gestionnaire only.
    """
    statement = select(Order).where(
        (Order.status == OrderStatus.PENDING) | 
        (Order.status == OrderStatus.VALIDATED)
    ).where(Order.livreur_id == None)
    
    orders = session.exec(statement.offset(skip).limit(limit)).all()
    return orders

@router.patch("/{id}/status", response_model=OrderRead)
def update_order_status(
    *,
    session: Session = Depends(get_session),
    id: int,
    order_update: OrderStatusUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update order status. Only for staff.
    """
    if current_user.role not in ["admin", "gestionnaire", "livreur"]:
        raise HTTPException(status_code=403, detail="Permissions insuffisantes")
    
    order = session.get(Order, id)
    if not order:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    
    # Livreur can only update their assigned orders
    if current_user.role == "livreur" and order.livreur_id != current_user.id:
        raise HTTPException(status_code=403, detail="Vous ne pouvez modifier que vos commandes assignées")
    
    order.status = order_update.status
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
    """
    Assign an order to a delivery person.
    Admin et gestionnaire only.
    """
    order = session.get(Order, id)
    if not order:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    
    # Verify the livreur exists and has the right role
    livreur = session.get(User, livreur_id)
    if not livreur:
        raise HTTPException(status_code=404, detail="Livreur non trouvé")
    
    if livreur.role != "livreur":
        raise HTTPException(status_code=400, detail="L'utilisateur spécifié n'est pas un livreur")
    
    if not livreur.is_approved:
        raise HTTPException(status_code=400, detail="Ce livreur n'est pas encore approuvé")
    
    # Assign the livreur and update status if pending
    order.livreur_id = livreur_id
    if order.status == OrderStatus.PENDING:
        order.status = OrderStatus.VALIDATED
    
    session.add(order)
    session.commit()
    session.refresh(order)
    return order

@router.get("/livreurs", response_model=List[dict])
def get_available_livreurs(
    session: Session = Depends(get_session),
    current_user: User = Depends(deps.get_current_admin_or_gestionnaire),
) -> Any:
    """
    Get list of available delivery persons for assignment.
    Admin et gestionnaire only.
    """
    livreurs = session.exec(
        select(User).where(User.role == "livreur").where(User.is_approved == True)
    ).all()
    
    return [{"id": l.id, "username": l.username, "email": l.email} for l in livreurs]
