from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.core.security import get_current_active_user
from app.db.session import get_db
from app.models import User, Team, TeamMember, Project, TestExecution, TestStatus, TestType
from app.schemas import (
    TestExecutionCreate, TestExecutionResponse, TestCase,
)
from app.workers.celery_app import run_tests_task

router = APIRouter()


@router.post("/{project_id}/run", response_model=TestExecutionResponse, status_code=status.HTTP_201_CREATED)
async def run_tests(
    project_id: UUID,
    test_data: TestExecutionCreate,
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
    
    execution = TestExecution(
        project_id=project_id,
        scan_session_id=test_data.scan_session_id,
        stabilization_task_id=test_data.stabilization_task_id,
        type=test_data.type,
        status=TestStatus.PENDING,
        tests=[],
        environment={},
    )
    db.add(execution)
    await db.commit()
    await db.refresh(execution)
    
    run_tests_task.delay(str(execution.id))
    return execution


@router.get("/{project_id}/executions", response_model=list[TestExecutionResponse])
async def list_test_executions(
    project_id: UUID,
    status_filter: Optional[TestStatus] = None,
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
    
    query = select(TestExecution).where(TestExecution.project_id == project_id)
    if status_filter:
        query = query.where(TestExecution.status == status_filter)
    
    result = await db.execute(query.order_by(TestExecution.started_at.desc()))
    executions = result.scalars().all()
    return executions


@router.get("/{project_id}/executions/{execution_id}", response_model=TestExecutionResponse)
async def get_test_execution(
    project_id: UUID,
    execution_id: UUID,
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
    
    execution_result = await db.execute(
        select(TestExecution).where(TestExecution.id == execution_id, TestExecution.project_id == project_id)
    )
    execution = execution_result.scalar_one_or_none()
    if not execution:
        raise HTTPException(status_code=404, detail="Test execution not found")
    
    return execution


@router.get("/{project_id}/executions/{execution_id}/report")
async def get_test_report(
    project_id: UUID,
    execution_id: UUID,
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
    
    execution_result = await db.execute(
        select(TestExecution).where(TestExecution.id == execution_id, TestExecution.project_id == project_id)
    )
    execution = execution_result.scalar_one_or_none()
    if not execution:
        raise HTTPException(status_code=404, detail="Test execution not found")
    
    return {
        "execution_id": str(execution.id),
        "type": execution.type,
        "status": execution.status,
        "summary": {
            "passed": execution.passed_count,
            "failed": execution.failed_count,
            "skipped": execution.skipped_count,
            "total": execution.passed_count + execution.failed_count + execution.skipped_count,
            "duration": execution.total_duration,
        },
        "tests": execution.tests,
        "environment": execution.environment,
        "started_at": execution.started_at.isoformat(),
        "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
    }


@router.post("/{project_id}/executions/{execution_id}/retry")
async def retry_test_execution(
    project_id: UUID,
    execution_id: UUID,
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
    
    execution_result = await db.execute(
        select(TestExecution).where(TestExecution.id == execution_id, TestExecution.project_id == project_id)
    )
    execution = execution_result.scalar_one_or_none()
    if not execution:
        raise HTTPException(status_code=404, detail="Test execution not found")
    
    new_execution = TestExecution(
        project_id=project_id,
        scan_session_id=execution.scan_session_id,
        stabilization_task_id=execution.stabilization_task_id,
        type=execution.type,
        status=TestStatus.PENDING,
        tests=[],
        environment=execution.environment,
    )
    db.add(new_execution)
    await db.commit()
    await db.refresh(new_execution)
    
    run_tests_task.delay(str(new_execution.id))
    return {"message": "Test retry started", "execution_id": str(new_execution.id)}