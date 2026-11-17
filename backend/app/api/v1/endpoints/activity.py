from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from uuid import UUID

from app.core.security import get_current_active_user
from app.db.session import get_db
from app.models import User, Team, TeamMember, Project, ActivityLog
from app.schemas import ActivityLogResponse, PaginatedResponse

router = APIRouter()


@router.get("/{project_id}", response_model=PaginatedResponse[ActivityLogResponse])
async def list_activity(
    project_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id)
        .join(TeamMember, Project.team_id == TeamMember.team_id)
        .where(TeamMember.user_id == current_user.id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    query = select(ActivityLog).where(ActivityLog.project_id == project_id)
    if action:
        query = query.where(ActivityLog.action == action)
    if entity_type:
        query = query.where(ActivityLog.entity_type == entity_type)
    
    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar()
    
    result = await db.execute(
        query.order_by(ActivityLog.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .options(selectinload(ActivityLog.user))
    )
    activities = result.scalars().all()
    
    return PaginatedResponse(
        items=activities,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/{project_id}/{activity_id}", response_model=ActivityLogResponse)
async def get_activity(
    project_id: UUID,
    activity_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id)
        .join(TeamMember, Project.team_id == TeamMember.team_id)
        .where(TeamMember.user_id == current_user.id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    activity_result = await db.execute(
        select(ActivityLog)
        .where(ActivityLog.id == activity_id, ActivityLog.project_id == project_id)
        .options(selectinload(ActivityLog.user))
    )
    activity = activity_result.scalar_one_or_none()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    return activity