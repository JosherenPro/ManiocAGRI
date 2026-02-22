import httpx
import logging
from typing import Optional, Dict, Any
from core.config import settings
from models.transaction import TransactionStatus

logger = logging.getLogger(__name__)

class PaymentService:
    @staticmethod
    async def initiate_payment(
        order_number: str,
        amount: int,
        phone_number: str,
        network: str,
        description: str = "Paiement commande ManiocAgri"
    ) -> Dict[str, Any]:
        """
        Initiates a payment request using PayGateGlobal API (Method 1).
        :param order_number: Unique identifier for the transaction
        :param amount: Amount in FCFA
        :param phone_number: Client phone number
        :param network: FLOOZ or TMONEY
        :param description: Optional description
        :return: Response from PayGate API
        """
        payload = {
            "auth_token": settings.PAYGATE_API_KEY,
            "phone_number": phone_number,
            "amount": amount,
            "description": description,
            "identifier": order_number,
            "network": network.upper()
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(settings.PAYGATE_PAY_URL, json=payload, timeout=30.0)
                response.raise_for_status()
                data = response.json()
                logger.info(f"PayGate Initiation Response for {order_number}: {data}")
                return data
        except Exception as e:
            logger.error(f"Error initiating PayGate payment for {order_number}: {str(e)}")
            return {"status": -1, "error": str(e)}

    @staticmethod
    async def check_payment_status(tx_reference: str) -> Dict[str, Any]:
        """
        Checks the status of a transaction using tx_reference.
        """
        payload = {
            "auth_token": settings.PAYGATE_API_KEY,
            "tx_reference": tx_reference
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(settings.PAYGATE_STATUS_URL, json=payload, timeout=30.0)
                response.raise_for_status()
                data = response.json()
                logger.info(f"PayGate Status Check for {tx_reference}: {data}")
                return data
        except Exception as e:
            logger.error(f"Error checking PayGate status for {tx_reference}: {str(e)}")
            return {"status": -1, "error": str(e)}

    @staticmethod
    def map_paygate_status(status_code: int) -> TransactionStatus:
        """
        Maps PayGate status codes to internal TransactionStatus.
        0 : Paiement réussi avec succès
        2 : En cours
        4 : Expiré
        6 : Annulé
        """
        mapping = {
            0: TransactionStatus.SUCCESS,
            2: TransactionStatus.PENDING,
            4: TransactionStatus.FAILED,
            6: TransactionStatus.FAILED  # Or custom CANCELED if added
        }
        return mapping.get(status_code, TransactionStatus.FAILED)

payment_service = PaymentService()
