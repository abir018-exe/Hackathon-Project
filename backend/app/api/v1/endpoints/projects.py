from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from uuid import UUID
import os
import shutil
import zipfile
import tempfile
from pathlib import Path

from app.core.security import get_current_active_user
from app.db.session import get_db
from app.models import User, Team, TeamMember, Project, ProjectStatus
from app.schemas import (
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse,
    PaginatedResponse,
)
from app.core.config import settings
from app.workers.celery_app import scan_project_task

router = APIRouter()


def check_team_access(team_id: UUID, user_id: UUID, db: AsyncSession, required_roles: List[str] = None) -> TeamMember:
    if required_roles is None:
        required_roles = ["owner", "admin", "developer", "viewer"]
    result = db.execute(
        select(TeamMember).where(TeamMember.team_id == team_id, TeamMember.user_id == user_id)
    )
    member = result.scalar_one_or_none()
    if not member or member.role not in required_roles:
        raise HTTPException(status_code=403, detail="Not authorized for this team")
    return member


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    check_team_access(project_data.team_id, current_user.id, db)
    
    project = Project(
        name=project_data.name,
        description=project_data.description,
        team_id=project_data.team_id,
        repository_url=str(project_data.repository_url) if project_data.repository_url else None,
        branch=project_data.branch,
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    team_id: Optional[UUID] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[ProjectStatus] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Project).join(TeamMember, Project.team_id == TeamMember.team_id).where(
        TeamMember.user_id == current_user.id
    )
    
    if team_id:
        query = query.where(Project.team_id == team_id)
    if status_filter:
        query = query.where(Project.status == status_filter)
    
    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar()
    
    result = await db.execute(
        query.order_by(Project.updated_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    projects = result.scalars().all()
    
    return ProjectListResponse(
        items=projects,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
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
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    project_data: ProjectUpdate,
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
        raise HTTPException(status_code=404, detail="Project not found or not authorized")
    
    if project_data.name is not None:
        project.name = project_data.name
    if project_data.description is not None:
        project.description = project_data.description
    if project_data.repository_url is not None:
        project.repository_url = str(project_data.repository_url)
    if project_data.branch is not None:
        project.branch = project_data.branch
    if project_data.framework is not None:
        project.framework = project_data.framework
    if project_data.language is not None:
        project.language = project_data.language
    
    await db.commit()
    await db.refresh(project)
    return project


@router.delete("/{project_id}")
async def delete_project(
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
        raise HTTPException(status_code=404, detail="Project not found or not authorized")
    
    if project.storage_path and os.path.exists(project.storage_path):
        shutil.rmtree(project.storage_path)
    
    await db.delete(project)
    await db.commit()
    return {"message": "Project deleted"}


@router.post("/{project_id}/upload", response_model=ProjectResponse)
async def upload_project_zip(
    project_id: UUID,
    file: UploadFile = File(...),
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
        raise HTTPException(status_code=404, detail="Project not found or not authorized")
    
    if not file.filename.endswith(tuple(settings.ALLOWED_ARCHIVE_EXTENSIONS)):
        raise HTTPException(status_code=400, detail="Invalid file type. Allowed: .zip, .tar, .tar.gz, .tgz")
    
    storage_base = Path(settings.PROJECT_STORAGE_PATH)
    storage_base.mkdir(parents=True, exist_ok=True)
    project_storage = storage_base / str(project_id)
    project_storage.mkdir(exist_ok=True)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
        content = await file.read()
        if len(content) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
            raise HTTPException(status_code=400, detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE_MB}MB")
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        if project.storage_path and os.path.exists(project.storage_path):
            shutil.rmtree(project.storage_path)
        
        project.storage_path = str(project_storage)
        
        with zipfile.ZipFile(tmp_path, 'r') as zip_ref:
            zip_ref.extractall(project_storage)
        
        project.status = ProjectStatus.PENDING
        await db.commit()
        await db.refresh(project)
        
        scan_project_task.delay(str(project_id))
        
        return project
    finally:
        os.unlink(tmp_path)


@router.post("/{project_id}/scan")
async def scan_project(
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
    
    scan_project_task.delay(str(project_id))
    return {"message": "Scan started"}


@router.get("/{project_id}/scan/status")
async def get_scan_status(
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
    
    from app.models import ScanSession
    scan_result = await db.execute(
        select(ScanSession)
        .where(ScanSession.project_id == project_id)
        .order_by(ScanSession.started_at.desc())
        .limit(1)
    )
    scan = scan_result.scalar_one_or_none()
    
    if not scan:
        return {"status": "not_started"}
    
    return {
        "scan_id": str(scan.id),
        "status": scan.status,
        "progress": scan.progress,
        "current_step": scan.current_step,
        "total_files": scan.total_files,
        "scanned_files": scan.scanned_files,
    }


@router.get("/{project_id}/scan/results")
async def get_scan_results(
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
    
    from app.models import ScanSession, ScanFinding, SecretFinding
    scan_result = await db.execute(
        select(ScanSession)
        .where(ScanSession.project_id == project_id)
        .order_by(ScanSession.started_at.desc())
        .limit(1)
    )
    scan = scan_result.scalar_one_or_none()
    
    if not scan:
        raise HTTPException(status_code=404, detail="No scan found")
    
    findings_result = await db.execute(
        select(ScanFinding).where(ScanFinding.scan_session_id == scan.id)
    )
    findings = findings_result.scalars().all()
    
    secrets_result = await db.execute(
        select(SecretFinding).where(SecretFinding.scan_session_id == scan.id)
    )
    secrets = secrets_result.scalars().all()
    
    return {
        "scan_id": str(scan.id),
        "status": scan.status,
        "languages": scan.languages,
        "frameworks": scan.frameworks,
        "dependencies": scan.dependencies,
        "issues": [
            {
                "id": str(f.id),
                "type": f.type,
                "category": f.category,
                "file": f.file,
                "line": f.line,
                "column": f.column,
                "message": f.message,
                "rule": f.rule,
                "fixable": f.fixable,
            }
            for f in findings
        ],
        "secrets": [
            {
                "id": str(s.id),
                "type": s.type,
                "file": s.file,
                "line": s.line,
                "severity": s.severity,
                "matched_content": s.matched_content,
            }
            for s in secrets
        ],
    }


@router.get("/{project_id}/dashboard")
async def get_project_dashboard(
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
    
    from app.models import RiskAssessment, Feature, StabilizationTask, TestExecution, GitCommit
    
    risk_result = await db.execute(
        select(RiskAssessment)
        .where(RiskAssessment.project_id == project_id)
        .order_by(RiskAssessment.created_at.desc())
        .limit(1)
    )
    risk = risk_result.scalar_one_or_none()
    
    features_result = await db.execute(
        select(Feature).where(Feature.project_id == project_id)
    )
    features = features_result.scalars().all()
    
    tasks_result = await db.execute(
        select(StabilizationTask).where(StabilizationTask.project_id == project_id)
    )
    tasks = tasks_result.scalars().all()
    
    tests_result = await db.execute(
        select(TestExecution).where(TestExecution.project_id == project_id)
    )
    tests = tests_result.scalars().all()
    
    commits_result = await db.execute(
        select(GitCommit).where(GitCommit.project_id == project_id)
        .order_by(GitCommit.timestamp.desc())
        .limit(10)
    )
    commits = commits_result.scalars().all()
    
    return {
        "project": project,
        "risk_assessment": risk,
        "features": features,
        "stabilization_tasks": tasks,
        "test_executions": tests,
        "recent_commits": commits,
    }