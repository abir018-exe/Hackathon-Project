from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID

from app.core.security import get_current_active_user
from app.db.session import get_db
from app.models import User, Notification, NotificationType
from app.schemas import NotificationResponse, PaginatedResponse

router = APIRouter()


@router.get("", response_model=PaginatedResponse[NotificationResponse])
async def list_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    unread_only: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Notification).where(Notification.user_id == current_user.id)
    if unread_only:
        query = query.where(Notification.read == False)
    
    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar()
    
    result = await db.execute(
        query.order_by(Notification.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    notifications = result.scalars().all()
    
    return PaginatedResponse(
        items=notifications,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Notification)
        .where(Notification.id == notification_id, Notification.user_id == current_user.id)
    )
    notification = result.scalar_one_or_none()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.read = True
    await db.commit()
    return {"message": "Notification marked as read"}


@router.post("/read-all")
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == current_user.id, Notification.read == False)
    )
    notifications = result.scalars().all()
    
    for notification in notifications:
        notification.read = True
    
    await db.commit()
    return {"message": f"Marked {len(notifications)} notifications as read"}