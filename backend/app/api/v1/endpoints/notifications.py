from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from api import deps
from core.db import get_session
from models.user import User
from models.notification import Notification, NotificationCreate, NotificationRead

router = APIRouter()


@router.get("/", response_model=List[NotificationRead])
def read_notifications(
    session: Session = Depends(get_session),
    current_user: User = Depends(deps.get_current_user),
    unread_only: bool = False,
    skip: int = 0,
    limit: int = 50,
) -> Any:
    """List notifications for the current user."""
    statement = select(Notification).where(Notification.user_id == current_user.id)
    if unread_only:
        statement = statement.where(Notification.is_read == False)
    statement = statement.order_by(Notification.created_at.desc()).offset(skip).limit(limit)
    return session.exec(statement).all()


@router.get("/unread-count")
def get_unread_count(
    session: Session = Depends(get_session),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Return the number of unread notifications."""
    from sqlmodel import func
    count = session.exec(
        select(func.count(Notification.id))
        .where(Notification.user_id == current_user.id)
        .where(Notification.is_read == False)
    ).one()
    return {"unread_count": count}


@router.patch("/{id}/read", response_model=NotificationRead)
def mark_as_read(
    *,
    session: Session = Depends(get_session),
    id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Mark a notification as read."""
    notif = session.get(Notification, id)
    if not notif or notif.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Notification non trouvée")
    notif.is_read = True
    session.add(notif)
    session.commit()
    session.refresh(notif)
    return notif


@router.patch("/read-all")
def mark_all_as_read(
    session: Session = Depends(get_session),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Mark all notifications as read."""
    notifs = session.exec(
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .where(Notification.is_read == False)
    ).all()
    for n in notifs:
        n.is_read = True
        session.add(n)
    session.commit()
    return {"updated": len(notifs)}


@router.delete("/{id}")
def delete_notification(
    *,
    session: Session = Depends(get_session),
    id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Delete a notification."""
    notif = session.get(Notification, id)
    if not notif or notif.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Notification non trouvée")
    session.delete(notif)
    session.commit()
    return {"deleted": True}


@router.post("/", response_model=NotificationRead)
def create_notification(
    *,
    session: Session = Depends(get_session),
    notif_in: NotificationCreate,
    current_user: User = Depends(deps.get_current_admin_or_gestionnaire),
) -> Any:
    """Create a notification for a specific user. Admin/Gestionnaire only."""
    db_notif = Notification.from_orm(notif_in)
    session.add(db_notif)
    session.commit()
    session.refresh(db_notif)
    return db_notif
