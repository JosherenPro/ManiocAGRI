from datetime import datetime
from enum import Enum
from typing import Optional
from sqlmodel import Field, SQLModel


class TransactionStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"


class TransactionPaymentMethod(str, Enum):
    MOBILE_YASS = "Mobile Yass"
    VISA = "Visa"
    MOOV_MONEY = "Moov Money"
    CASH = "Espèces"


class TransactionBase(SQLModel):
    order_id: int = Field(foreign_key="order.id", index=True)
    amount: int  # FCFA
    payment_method: TransactionPaymentMethod
    status: TransactionStatus = Field(default=TransactionStatus.PENDING)
    reference: Optional[str] = Field(default=None, index=True)  # external transaction ref
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Transaction(TransactionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class TransactionCreate(SQLModel):
    order_id: int
    amount: int
    payment_method: TransactionPaymentMethod
    reference: Optional[str] = None
    notes: Optional[str] = None


class TransactionRead(TransactionBase):
    id: int


class TransactionUpdate(SQLModel):
    status: Optional[TransactionStatus] = None
    reference: Optional[str] = None
    notes: Optional[str] = None
