from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session, select
from core.db import get_session
from models.order import Order
from models.transaction import Transaction, TransactionStatus, TransactionPaymentMethod
from services.payment_service import payment_service
from typing import Any
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/initiate")
async def initiate_payment(
    order_id: int = Body(...),
    phone_number: str = Body(...),
    network: str = Body(...),  # FLOOZ or TMONEY
    session: Session = Depends(get_session)
) -> Any:
    """
    Endpoint to initiate a mobile payment via PayGateGlobal.
    """
    # 1. Fetch Order
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    
    if order.paid:
        raise HTTPException(status_code=400, detail="Cette commande est déjà payée")

    # 2. Initiate with PayGate
    amount = order.total_price
    # Ensure amount is valid
    if amount <= 0:
         raise HTTPException(status_code=400, detail="Montant de la commande invalide")

    result = await payment_service.initiate_payment(
        order_number=order.order_number,
        amount=amount,
        phone_number=phone_number,
        network=network
    )

    # Status 0 means success in registration
    if result.get("status") != 0:
        logger.error(f"PayGate Initiation Failed for Order {order.order_number}: {result}")
        raise HTTPException(
            status_code=400, 
            detail=f"Échec de l'initiation du paiement: {result.get('error', 'Erreur technique')}"
        )

    # 3. Create or Update Transaction record
    tx_ref = result.get("tx_reference")
    
    # Map network string to Enum
    network_upper = network.upper()
    if network_upper == "FLOOZ":
        pm = TransactionPaymentMethod.FLOOZ
    elif network_upper == "TMONEY":
        pm = TransactionPaymentMethod.TMONEY
    else:
        pm = TransactionPaymentMethod.MOBILE_YASS # Fallback

    transaction = Transaction(
        order_id=order.id,
        amount=amount,
        payment_method=pm,
        status=TransactionStatus.PENDING,
        reference=tx_ref,
        notes=f"Paiement initié via {network_upper}"
    )
    
    # Update order payment method too
    order.payment_method = pm.value
    
    session.add(transaction)
    session.add(order)
    session.commit()
    session.refresh(transaction)

    return {
        "status": "success",
        "message": "Paiement initié. Veuillez confirmer la transaction sur votre téléphone.",
        "transaction_id": transaction.id,
        "tx_reference": tx_ref
    }
