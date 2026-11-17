from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID

from app.core.security import get_current_active_user
from app.db.session import get_db
from app.models import User, Team, TeamMember, Project, StabilizationTask, Patch, TaskStatus, TaskType, RiskLevel
from app.schemas import (
    StabilizationTaskCreate, StabilizationTaskUpdate, StabilizationTaskResponse,
    StabilizationFile, PatchResponse,
)
from app.workers.celery_app import apply_patches_task

router = APIRouter()


@router.post("/{project_id}/tasks", response_model=StabilizationTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_stabilization_task(
    project_id: UUID,
    task_data: StabilizationTaskCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id)
        .join(TeamMember, Project.team_id == TeamMember.team_id)
        .where(TeamMember.user_id == current_user.id, TeamMember.role.in_(["owner", "admin", "developer"]))
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    task = StabilizationTask(
        project_id=project_id,
        title=task_data.title,
        description=task_data.description,
        type=task_data.type,
        priority=task_data.priority,
        files=[f.model_dump() for f in task_data.files],
        ai_recommendation_id=task_data.ai_recommendation_id,
        created_by=current_user.id,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


@router.get("/{project_id}/tasks", response_model=List[StabilizationTaskResponse])
async def list_stabilization_tasks(
    project_id: UUID,
    status_filter: Optional[TaskStatus] = None,
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
    
    query = select(StabilizationTask).where(StabilizationTask.project_id == project_id)
    if status_filter:
        query = query.where(StabilizationTask.status == status_filter)
    
    result = await db.execute(query.order_by(StabilizationTask.created_at.desc()))
    tasks = result.scalars().all()
    return tasks


@router.get("/{project_id}/tasks/{task_id}", response_model=StabilizationTaskResponse)
async def get_stabilization_task(
    project_id: UUID,
    task_id: UUID,
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
    
    task_result = await db.execute(
        select(StabilizationTask).where(StabilizationTask.id == task_id, StabilizationTask.project_id == project_id)
    )
    task = task_result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task


@router.put("/{project_id}/tasks/{task_id}", response_model=StabilizationTaskResponse)
async def update_stabilization_task(
    project_id: UUID,
    task_id: UUID,
    task_data: StabilizationTaskUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id)
        .join(TeamMember, Project.team_id == TeamMember.team_id)
        .where(TeamMember.user_id == current_user.id, TeamMember.role.in_(["owner", "admin", "developer"]))
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    task_result = await db.execute(
        select(StabilizationTask).where(StabilizationTask.id == task_id, StabilizationTask.project_id == project_id)
    )
    task = task_result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description
    if task_data.status is not None:
        task.status = task_data.status
    if task_data.priority is not None:
        task.priority = task_data.priority
    if task_data.files is not None:
        task.files = [f.model_dump() for f in task_data.files]
    
    await db.commit()
    await db.refresh(task)
    return task


@router.post("/{project_id}/tasks/{task_id}/patches/{patch_id}/approve")
async def approve_patch(
    project_id: UUID,
    task_id: UUID,
    patch_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id)
        .join(TeamMember, Project.team_id == TeamMember.team_id)
        .where(TeamMember.user_id == current_user.id, TeamMember.role.in_(["owner", "admin", "developer"]))
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    patch_result = await db.execute(
        select(Patch)
        .join(StabilizationTask, Patch.task_id == StabilizationTask.id)
        .where(Patch.id == patch_id, StabilizationTask.id == task_id, StabilizationTask.project_id == project_id)
    )
    patch = patch_result.scalar_one_or_none()
    if not patch:
        raise HTTPException(status_code=404, detail="Patch not found")
    
    patch.status = "approved"
    patch.approved_by = current_user.id
    patch.applied_at = None
    
    task_result = await db.execute(
        select(StabilizationTask).where(StabilizationTask.id == task_id)
    )
    task = task_result.scalar_one_or_none()
    if task:
        all_approved = all(p.status == "approved" for p in task.patches)
        if all_approved and task.patches:
            task.status = TaskStatus.APPROVED
    
    await db.commit()
    return {"message": "Patch approved"}


@router.post("/{project_id}/tasks/{task_id}/patches/{patch_id}/reject")
async def reject_patch(
    project_id: UUID,
    task_id: UUID,
    patch_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id)
        .join(TeamMember, Project.team_id == TeamMember.team_id)
        .where(TeamMember.user_id == current_user.id, TeamMember.role.in_(["owner", "admin", "developer"]))
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    patch_result = await db.execute(
        select(Patch)
        .join(StabilizationTask, Patch.task_id == StabilizationTask.id)
        .where(Patch.id == patch_id, StabilizationTask.id == task_id, StabilizationTask.project_id == project_id)
    )
    patch = patch_result.scalar_one_or_none()
    if not patch:
        raise HTTPException(status_code=404, detail="Patch not found")
    
    patch.status = "rejected"
    
    await db.commit()
    return {"message": "Patch rejected"}


@router.post("/{project_id}/tasks/{task_id}/apply")
async def apply_patches(
    project_id: UUID,
    task_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id)
        .join(TeamMember, Project.team_id == TeamMember.team_id)
        .where(TeamMember.user_id == current_user.id, TeamMember.role.in_(["owner", "admin", "developer"]))
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    task_result = await db.execute(
        select(StabilizationTask).where(StabilizationTask.id == task_id, StabilizationTask.project_id == project_id)
    )
    task = task_result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status != TaskStatus.APPROVED:
        raise HTTPException(status_code=400, detail="Task must be approved before applying")
    
    apply_patches_task.delay(str(task_id))
    return {"message": "Patches application started"}


@router.post("/{project_id}/tasks/{task_id}/rollback")
async def rollback_task(
    project_id: UUID,
    task_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id)
        .join(TeamMember, Project.team_id == TeamMember.team_id)
        .where(TeamMember.user_id == current_user.id, TeamMember.role.in_(["owner", "admin", "developer"]))
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    task_result = await db.execute(
        select(StabilizationTask).where(StabilizationTask.id == task_id, StabilizationTask.project_id == project_id)
    )
    task = task_result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status != TaskStatus.APPLIED:
        raise HTTPException(status_code=400, detail="Can only rollback applied tasks")
    
    task.status = TaskStatus.ROLLED_BACK
    task.rolled_back_at = datetime.utcnow()
    
    for patch in task.patches:
        if patch.status == "applied":
            patch.status = "rolled_back"
            patch.rolled_back_at = datetime.utcnow()
    
    await db.commit()
    return {"message": "Task rolled back"}


@router.get("/{project_id}/history")
async def get_stabilization_history(
    project_id: UUID,
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
    
    tasks_result = await db.execute(
        select(StabilizationTask)
        .where(StabilizationTask.project_id == project_id)
        .order_by(StabilizationTask.created_at.desc())
    )
    tasks = tasks_result.scalars().all()
    
    return {"tasks": tasks}