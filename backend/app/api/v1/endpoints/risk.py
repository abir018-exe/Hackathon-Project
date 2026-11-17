from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from datetime import datetime

from app.core.security import get_current_active_user
from app.db.session import get_db
from app.models import User, Team, TeamMember, Project, GitCommit, RiskLevel
from app.schemas import GitCommitResponse, GitFileChange
from app.workers.celery_app import analyze_commit_task

router = APIRouter()


@router.get("/{project_id}/monitor")
async def get_risk_monitor(
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
    
    from app.models import RiskAssessment
    risk_result = await db.execute(
        select(RiskAssessment)
        .where(RiskAssessment.project_id == project_id)
        .order_by(RiskAssessment.created_at.desc())
        .limit(1)
    )
    risk = risk_result.scalar_one_or_none()
    
    commits_result = await db.execute(
        select(GitCommit)
        .where(GitCommit.project_id == project_id)
        .order_by(GitCommit.timestamp.desc())
        .limit(20)
    )
    commits = commits_result.scalars().all()
    
    risky_commits = [c for c in commits if c.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]]
    demo_path_commits = [c for c in commits if c.affects_demo_path]
    
    return {
        "project_id": str(project_id),
        "overall_risk": risk.risk_level if risk else RiskLevel.LOW,
        "demo_frozen": project.demo_readiness and project.demo_readiness >= 90,
        "recent_commits": len(commits),
        "risky_commits": len(risky_commits),
        "demo_path_changes": len(demo_path_commits),
        "latest_risky": [
            {
                "sha": c.sha[:8],
                "message": c.message[:100],
                "author": c.author,
                "timestamp": c.timestamp.isoformat(),
                "risk_level": c.risk_level,
                "risk_reason": c.risk_reason,
                "affects_demo_path": c.affects_demo_path,
            }
            for c in risky_commits[:5]
        ],
    }


@router.get("/{project_id}/commits", response_model=list[GitCommitResponse])
async def get_commits(
    project_id: UUID,
    limit: int = 50,
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
    
    commits_result = await db.execute(
        select(GitCommit)
        .where(GitCommit.project_id == project_id)
        .order_by(GitCommit.timestamp.desc())
        .limit(limit)
    )
    commits = commits_result.scalars().all()
    return commits


@router.post("/{project_id}/freeze")
async def freeze_demo(
    project_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id)
        .join(TeamMember, Project.team_id == TeamMember.team_id)
        .where(TeamMember.user_id == current_user.id, TeamMember.role.in_(["owner", "admin"]))
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.demo_readiness is None or project.demo_readiness < 80:
        raise HTTPException(status_code=400, detail="Demo readiness must be at least 80% to freeze")
    
    project.demo_readiness = 100
    await db.commit()
    return {"message": "Demo frozen - no further changes allowed without approval"}


@router.post("/{project_id}/unfreeze")
async def unfreeze_demo(
    project_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id)
        .join(TeamMember, Project.team_id == TeamMember.team_id)
        .where(TeamMember.user_id == current_user.id, TeamMember.role.in_(["owner", "admin"]))
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project.demo_readiness = 90
    await db.commit()
    return {"message": "Demo unfrozen - changes allowed"}


@router.post("/{project_id}/commits/{sha}/analyze")
async def analyze_commit(
    project_id: UUID,
    sha: str,
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
    
    analyze_commit_task.delay(str(project_id), sha)
    return {"message": "Commit analysis started"}