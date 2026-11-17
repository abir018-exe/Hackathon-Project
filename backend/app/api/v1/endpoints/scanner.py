from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from uuid import UUID

from app.core.security import get_current_active_user
from app.db.session import get_db
from app.models import User, Team, TeamMember, Project, ScanSession, ScanFinding, SecretFinding, ScanStatus
from app.schemas import (
    ScanSessionResponse, ScanSessionUpdate,
    LanguageStats, FrameworkStats, DependencyStats, ScanIssue, SecretFinding as SecretFindingSchema,
    PaginatedResponse,
)
from app.workers.celery_app import scan_project_task

router = APIRouter()


@router.post("/upload")
async def upload_and_scan(
    project_id: UUID,
    file: UploadFile,
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
    
    scan_project_task.delay(str(project_id))
    return {"message": "Scan started"}


@router.get("/{scan_id}", response_model=ScanSessionResponse)
async def get_scan_session(
    scan_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ScanSession)
        .where(ScanSession.id == scan_id)
        .join(Project, ScanSession.project_id == Project.id)
        .join(TeamMember, Project.team_id == TeamMember.team_id)
        .where(TeamMember.user_id == current_user.id)
    )
    scan = result.scalar_one_or_none()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan


@router.get("/{scan_id}/status")
async def get_scan_status(
    scan_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ScanSession)
        .where(ScanSession.id == scan_id)
        .join(Project, ScanSession.project_id == Project.id)
        .join(TeamMember, Project.team_id == TeamMember.team_id)
        .where(TeamMember.user_id == current_user.id)
    )
    scan = result.scalar_one_or_none()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    return {
        "scan_id": str(scan.id),
        "status": scan.status,
        "progress": scan.progress,
        "current_step": scan.current_step,
        "total_files": scan.total_files,
        "scanned_files": scan.scanned_files,
    }


@router.get("/{scan_id}/results")
async def get_scan_results(
    scan_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ScanSession)
        .where(ScanSession.id == scan_id)
        .join(Project, ScanSession.project_id == Project.id)
        .join(TeamMember, Project.team_id == TeamMember.team_id)
        .where(TeamMember.user_id == current_user.id)
    )
    scan = result.scalar_one_or_none()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
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


@router.get("/{scan_id}/file-tree")
async def get_file_tree(
    scan_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ScanSession)
        .where(ScanSession.id == scan_id)
        .join(Project, ScanSession.project_id == Project.id)
        .join(TeamMember, Project.team_id == TeamMember.team_id)
        .where(TeamMember.user_id == current_user.id)
    )
    scan = result.scalar_one_or_none()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    if not scan.project.storage_path:
        raise HTTPException(status_code=404, detail="Project files not available")
    
    from pathlib import Path
    import os
    
    def build_tree(path: Path, root: Path):
        rel_path = path.relative_to(root)
        if path.is_file():
            return {
                "name": path.name,
                "path": str(rel_path),
                "type": "file",
                "size": path.stat().st_size,
            }
        else:
            children = []
            try:
                for child in sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name.lower())):
                    if not child.name.startswith('.') and child.name not in ['node_modules', '__pycache__', '.git', 'venv', 'env', 'dist', 'build']:
                        children.append(build_tree(child, root))
            except PermissionError:
                pass
            return {
                "name": path.name if path != root else root.name,
                "path": str(rel_path) if path != root else "",
                "type": "directory",
                "children": children,
            }
    
    tree = build_tree(Path(scan.project.storage_path), Path(scan.project.storage_path))
    return tree


@router.get("/{scan_id}/file-content")
async def get_file_content(
    scan_id: UUID,
    path: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ScanSession)
        .where(ScanSession.id == scan_id)
        .join(Project, ScanSession.project_id == Project.id)
        .join(TeamMember, Project.team_id == TeamMember.team_id)
        .where(TeamMember.user_id == current_user.id)
    )
    scan = result.scalar_one_or_none()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    if not scan.project.storage_path:
        raise HTTPException(status_code=404, detail="Project files not available")
    
    from pathlib import Path
    file_path = Path(scan.project.storage_path) / path
    
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        content = file_path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        content = "[Binary file - cannot display]"
    
    return {"path": path, "content": content}