from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.core.security import get_current_active_user
from app.db.session import get_db
from app.models import User, Team, TeamMember, Project, DemoScript
from app.schemas import (
    DemoScriptCreate, DemoScriptUpdate, DemoScriptResponse, DemoScriptSection,
)
from app.workers.celery_app import generate_demo_script_task

router = APIRouter()


@router.post("/{project_id}/generate", response_model=DemoScriptResponse, status_code=status.HTTP_201_CREATED)
async def generate_demo_script(
    project_id: UUID,
    script_data: DemoScriptCreate,
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
    
    script = DemoScript(
        project_id=project_id,
        title=script_data.title,
        duration_minutes=script_data.duration_minutes,
        audience=script_data.audience,
        sections=[s.model_dump() for s in script_data.sections],
        verified_features_only=script_data.verified_features_only,
    )
    db.add(script)
    await db.commit()
    await db.refresh(script)
    
    generate_demo_script_task.delay(str(script.id))
    return script


@router.get("/{project_id}", response_model=DemoScriptResponse)
async def get_demo_script(
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
    
    script_result = await db.execute(
        select(DemoScript)
        .where(DemoScript.project_id == project_id)
        .order_by(DemoScript.generated_at.desc())
        .limit(1)
    )
    script = script_result.scalar_one_or_none()
    if not script:
        raise HTTPException(status_code=404, detail="No demo script found. Generate one first.")
    
    return script


@router.put("/{project_id}", response_model=DemoScriptResponse)
async def update_demo_script(
    project_id: UUID,
    script_data: DemoScriptUpdate,
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
    
    script_result = await db.execute(
        select(DemoScript)
        .where(DemoScript.project_id == project_id)
        .order_by(DemoScript.generated_at.desc())
        .limit(1)
    )
    script = script_result.scalar_one_or_none()
    if not script:
        raise HTTPException(status_code=404, detail="No demo script found")
    
    if script_data.title is not None:
        script.title = script_data.title
    if script_data.duration_minutes is not None:
        script.duration_minutes = script_data.duration_minutes
    if script_data.audience is not None:
        script.audience = script_data.audience
    if script_data.sections is not None:
        script.sections = [s.model_dump() for s in script_data.sections]
    if script_data.verified_features_only is not None:
        script.verified_features_only = script_data.verified_features_only
    
    await db.commit()
    await db.refresh(script)
    return script


@router.get("/{project_id}/export")
async def export_demo_script(
    project_id: UUID,
    format: str = Query("markdown", regex="^(markdown|pdf|html)$"),
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
    
    script_result = await db.execute(
        select(DemoScript)
        .where(DemoScript.project_id == project_id)
        .order_by(DemoScript.generated_at.desc())
        .limit(1)
    )
    script = script_result.scalar_one_or_none()
    if not script:
        raise HTTPException(status_code=404, detail="No demo script found")
    
    if format == "markdown":
        content = f"# {script.title}\n\n"
        content += f"**Duration:** {script.duration_minutes} minutes\n"
        content += f"**Audience:** {script.audience}\n\n"
        content += "---\n\n"
        
        for section in script.sections:
            content += f"## {section['title']}\n\n"
            content += f"**Duration:** {section['duration_minutes']} minutes\n\n"
            content += f"{section['content']}\n\n"
            
            if section.get('talking_points'):
                content += "**Talking Points:**\n"
                for point in section['talking_points']:
                    content += f"- {point}\n"
                content += "\n"
            
            if section.get('backup_content'):
                content += f"**Backup Plan:** {section['backup_content']}\n\n"
            
            content += "---\n\n"
        
        return {"format": "markdown", "content": content, "filename": f"{script.title.lower().replace(' ', '-')}.md"}
    
    return {"format": format, "content": "Export format not yet implemented", "filename": f"demo-script.{format}"}