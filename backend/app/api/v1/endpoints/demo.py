from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from datetime import datetime

from app.core.security import get_current_active_user
from app.db.session import get_db
from app.models import User, Team, TeamMember, Project, DemoConfiguration
from app.schemas import (
    DemoConfigurationCreate, DemoConfigurationUpdate, DemoConfigurationResponse,
    MockDataConfig, APIFallbackConfig, FeatureFlagConfig,
)

router = APIRouter()


@router.get("/{project_id}/config", response_model=DemoConfigurationResponse)
async def get_demo_config(
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
    
    config_result = await db.execute(
        select(DemoConfiguration).where(DemoConfiguration.project_id == project_id)
    )
    config = config_result.scalar_one_or_none()
    
    if not config:
        config = DemoConfiguration(project_id=project_id)
        db.add(config)
        await db.commit()
        await db.refresh(config)
    
    return config


@router.put("/{project_id}/config", response_model=DemoConfigurationResponse)
async def update_demo_config(
    project_id: UUID,
    config_data: DemoConfigurationUpdate,
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
    
    config_result = await db.execute(
        select(DemoConfiguration).where(DemoConfiguration.project_id == project_id)
    )
    config = config_result.scalar_one_or_none()
    
    if not config:
        config = DemoConfiguration(project_id=project_id)
        db.add(config)
    
    if config_data.name is not None:
        config.name = config_data.name
    if config_data.enabled is not None:
        config.enabled = config_data.enabled
    if config_data.mock_data is not None:
        config.mock_data = [m.model_dump() for m in config_data.mock_data]
    if config_data.api_fallbacks is not None:
        config.api_fallbacks = [a.model_dump() for a in config_data.api_fallbacks]
    if config_data.feature_flags is not None:
        config.feature_flags = [f.model_dump() for f in config_data.feature_flags]
    if config_data.environment_variables is not None:
        config.environment_variables = config_data.environment_variables
    
    await db.commit()
    await db.refresh(config)
    return config


@router.post("/{project_id}/activate")
async def activate_demo(
    project_id: UUID,
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
    
    config_result = await db.execute(
        select(DemoConfiguration).where(DemoConfiguration.project_id == project_id)
    )
    config = config_result.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="Demo configuration not found")
    
    config.enabled = True
    await db.commit()
    return {"message": "Demo mode activated", "config": config}


@router.post("/{project_id}/deactivate")
async def deactivate_demo(
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
    
    config_result = await db.execute(
        select(DemoConfiguration).where(DemoConfiguration.project_id == project_id)
    )
    config = config_result.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="Demo configuration not found")
    
    config.enabled = False
    await db.commit()
    return {"message": "Demo mode deactivated"}


@router.get("/{project_id}/status")
async def get_demo_status(
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
    
    config_result = await db.execute(
        select(DemoConfiguration).where(DemoConfiguration.project_id == project_id)
    )
    config = config_result.scalar_one_or_none()
    
    return {
        "enabled": config.enabled if config else False,
        "project_status": project.status,
        "demo_readiness": project.demo_readiness,
    }


@router.get("/{project_id}/preview")
async def preview_demo(
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
    
    from app.models import Feature
    features_result = await db.execute(
        select(Feature).where(Feature.project_id == project_id, Feature.demo_path == True)
    )
    features = features_result.scalars().all()
    
    return {
        "project_name": project.name,
        "demo_features": [
            {
                "id": str(f.id),
                "name": f.name,
                "path": f.path,
                "type": f.type,
                "reliability": f.reliability_score,
            }
            for f in features
        ],
    }


@router.post("/{project_id}/reset")
async def reset_demo(
    project_id: UUID,
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
    
    config_result = await db.execute(
        select(DemoConfiguration).where(DemoConfiguration.project_id == project_id)
    )
    config = config_result.scalar_one_or_none()
    if config:
        config.enabled = False
        config.mock_data = []
        config.api_fallbacks = []
        config.feature_flags = []
        config.environment_variables = {}
        await db.commit()
    
    return {"message": "Demo configuration reset"}