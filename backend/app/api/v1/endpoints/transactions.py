from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from api import deps
from core.db import get_session
from models.user import User
from models.transaction import Transaction, TransactionCreate, TransactionRead, TransactionUpdate

router = APIRouter()


@router.get("/", response_model=List[TransactionRead])
def read_transactions(
    session: Session = Depends(get_session),
    current_user: User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 50,
) -> Any:
    """
    List transactions.
    - Admin/Gestionnaire: see all.
    - Client: only transactions linked to their orders.
    """
    from models.order import Order

    statement = select(Transaction)
    if current_user.role not in ["admin", "gestionnaire"]:
        # Filter by orders belonging to this client
        client_order_ids = [
            o.id for o in session.exec(
                select(Order).where(Order.client_id == current_user.id)
            ).all()
        ]
        if not client_order_ids:
            return []
        statement = statement.where(Transaction.order_id.in_(client_order_ids))

    statement = statement.order_by(Transaction.created_at.desc()).offset(skip).limit(limit)
    return session.exec(statement).all()


@router.get("/{id}", response_model=TransactionRead)
def read_transaction(
    id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Get a single transaction by ID."""
    tx = session.get(Transaction, id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction non trouvée")
    # Authorization check
    if current_user.role not in ["admin", "gestionnaire"]:
        from models.order import Order
        order = session.get(Order, tx.order_id)
        if not order or order.client_id != current_user.id:
            raise HTTPException(status_code=403, detail="Accès refusé")
    return tx


@router.post("/", response_model=TransactionRead)
def create_transaction(
    *,
    session: Session = Depends(get_session),
    tx_in: TransactionCreate,
    current_user: User = Depends(deps.get_current_admin_or_gestionnaire),
) -> Any:
    """Record a new payment transaction. Admin/Gestionnaire only."""
    db_tx = Transaction.from_orm(tx_in)
    session.add(db_tx)
    session.commit()
    session.refresh(db_tx)
    return db_tx


@router.patch("/{id}", response_model=TransactionRead)
def update_transaction(
    *,
    session: Session = Depends(get_session),
    id: int,
    tx_in: TransactionUpdate,
    current_user: User = Depends(deps.get_current_admin_or_gestionnaire),
) -> Any:
    """Update a transaction status. Admin/Gestionnaire only."""
    tx = session.get(Transaction, id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction non trouvée")
    for key, value in tx_in.dict(exclude_unset=True).items():
        setattr(tx, key, value)
    session.add(tx)
    session.commit()
    session.refresh(tx)
    return tx
