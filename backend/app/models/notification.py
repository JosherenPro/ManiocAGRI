from datetime import datetime
from enum import Enum
from typing import Optional
from sqlmodel import Field, SQLModel


class NotificationType(str, Enum):
    ORDER_PLACED = "order_placed"
    ORDER_VALIDATED = "order_validated"
    ORDER_IN_TRANSIT = "order_in_transit"
    ORDER_DELIVERED = "order_delivered"
    ORDER_REJECTED = "order_rejected"
    PAYMENT_RECEIVED = "payment_received"
    USER_APPROVED = "user_approved"
    LOW_STOCK = "low_stock"
    NEW_REVIEW = "new_review"
    SYSTEM = "system"


class NotificationBase(SQLModel):
    user_id: int = Field(foreign_key="user.id", index=True)
    title: str
    message: str
    type: NotificationType = Field(default=NotificationType.SYSTEM)
    is_read: bool = Field(default=False)
    related_order_id: Optional[int] = Field(default=None, foreign_key="order.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Notification(NotificationBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class NotificationCreate(SQLModel):
    user_id: int
    title: str
    message: str
    type: NotificationType = NotificationType.SYSTEM
    related_order_id: Optional[int] = None


class NotificationRead(NotificationBase):
    id: int
