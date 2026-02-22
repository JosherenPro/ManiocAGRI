from fastapi import APIRouter, Depends, Request
from sqlmodel import Session, select
from core.db import get_session
from models.order import Order
from models.transaction import Transaction, TransactionStatus
from services.payment_service import payment_service
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/paygate")
async def paygate_webhook(
    request: Request,
    session: Session = Depends(get_session)
):
    """
    Webhook handler for PayGateGlobal payment confirmations.
    """
    try:
        data = await request.json()
    except Exception:
        logger.error("Failed to parse JSON from PayGate webhook")
        return {"status": "error", "message": "Invalid JSON"}

    logger.info(f"Received PayGate Webhook Confirmation: {data}")

    tx_reference = data.get("tx_reference")
    order_number = data.get("identifier")
    
    if not tx_reference:
        return {"status": "error", "message": "Missing tx_reference"}

    # 1. Double check the status with PayGate API (Security/Verification)
    status_check = await payment_service.check_payment_status(tx_reference)
    
    # status 0 = Success according to PayGate guide mappings
    if status_check.get("status") != 0:
        logger.warning(f"Webhook received for TX {tx_reference} but status is {status_check.get('status')} (Not Success)")
        return {"status": "ignored", "reason": "Not a successful transaction"}

    # 2. Find Transaction
    statement = select(Transaction).where(Transaction.reference == tx_reference)
    transaction = session.exec(statement).first()

    if not transaction and order_number:
        # Fallback search by order number
        statement = select(Order).where(Order.order_number == order_number)
        order = session.exec(statement).first()
        if order:
            # Look for a pending transaction for this order
            transaction = session.exec(
                select(Transaction).where(
                    Transaction.order_id == order.id, 
                    Transaction.status == TransactionStatus.PENDING
                )
            ).first()

    if transaction:
        if transaction.status == TransactionStatus.SUCCESS:
            logger.info(f"Transaction {tx_reference} already marked as SUCCESS.")
            return {"status": "ok", "message": "Already processed"}

        transaction.status = TransactionStatus.SUCCESS
        transaction.notes = f"Confirmé via webhook à {datetime.utcnow().isoformat()}"
        session.add(transaction)
        
        # 3. Update Order to 'Paid'
        order = session.get(Order, transaction.order_id)
        if order:
            order.paid = True
            session.add(order)
            logger.info(f"Order {order.order_number} marked as PAID via PayGate.")
        
        session.commit()
    else:
        logger.warning(f"No transaction found matching tx_reference: {tx_reference} or identifier: {order_number}")

    return {"status": "ok"}
