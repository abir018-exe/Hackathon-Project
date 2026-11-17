from typing: Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from datetime import datetime

from app.core.security import get_current_active_user
from app.db.session import get_db
from app.models import User, Team, TeamMember, Project, ScanSession, RiskAssessment, StabilizationTask, TestExecution, DemoConfiguration
from app.schemas import PaginatedResponse

router = APIRouter()


@router.get("/{project_id}/scan")
async def get_scan_report(
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
    
    scan_result = await db.execute(
        select(ScanSession)
        .where(ScanSession.project_id == project_id)
        .order_by(ScanSession.started_at.desc())
        .limit(1)
    )
    scan = scan_result.scalar_one_or_none()
    if not scan:
        raise HTTPException(status_code=404, detail="No scan found")
    
    from app.models import ScanFinding, SecretFinding
    findings_result = await db.execute(
        select(ScanFinding).where(ScanFinding.scan_session_id == scan.id)
    )
    findings = findings_result.scalars().all()
    
    secrets_result = await db.execute(
        select(SecretFinding).where(SecretFinding.scan_session_id == scan.id)
    )
    secrets = secrets_result.scalars().all()
    
    return {
        "project": {"id": str(project.id), "name": project.name},
        "scan": {
            "id": str(scan.id),
            "status": scan.status,
            "started_at": scan.started_at.isoformat(),
            "completed_at": scan.completed_at.isoformat() if scan.completed_at else None,
            "total_files": scan.total_files,
            "scanned_files": scan.scanned_files,
            "languages": scan.languages,
            "frameworks": scan.frameworks,
            "dependencies": scan.dependencies,
        },
        "summary": {
            "total_issues": len(findings),
            "errors": len([f for f in findings if f.type == "error"]),
            "warnings": len([f for f in findings if f.type == "warning"]),
            "info": len([f for f in findings if f.type == "info"]),
            "secrets_found": len(secrets),
        },
        "issues": [
            {
                "type": f.type,
                "category": f.category,
                "file": f.file,
                "line": f.line,
                "message": f.message,
                "rule": f.rule,
                "fixable": f.fixable,
            }
            for f in findings
        ],
        "secrets": [
            {
                "type": s.type,
                "file": s.file,
                "line": s.line,
                "severity": s.severity,
            }
            for s in secrets
        ],
    }


@router.get("/{project_id}/risk")
async def get_risk_report(
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
    
    risk_result = await db.execute(
        select(RiskAssessment)
        .where(RiskAssessment.project_id == project_id)
        .order_by(RiskAssessment.created_at.desc())
        .limit(1)
    )
    risk = risk_result.scalar_one_or_none()
    if not risk:
        raise HTTPException(status_code=404, detail="No risk assessment found")
    
    return {
        "project": {"id": str(project.id), "name": project.name},
        "overall_score": risk.overall_score,
        "risk_level": risk.risk_level,
        "risk_distribution": risk.risk_distribution,
        "feature_scores": risk.feature_scores,
        "failure_predictions": risk.failure_predictions,
        "happy_paths": risk.happy_paths,
        "dependency_risks": risk.dependency_risks,
        "ai_recommendations": risk.ai_recommendations,
        "generated_at": risk.created_at.isoformat(),
    }


@router.get("/{project_id}/stabilization")
async def get_stabilization_report(
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
        select(StabilizationTask).where(StabilizationTask.project_id == project_id)
    )
    tasks = tasks_result.scalars().all()
    
    return {
        "project": {"id": str(project.id), "name": project.name},
        "total_tasks": len(tasks),
        "by_status": {
            "pending": len([t for t in tasks if t.status == "pending"]),
            "approved": len([t for t in tasks if t.status == "approved"]),
            "rejected": len([t for t in tasks if t.status == "rejected"]),
            "applied": len([t for t in tasks if t.status == "applied"]),
            "rolled_back": len([t for t in tasks if t.status == "rolled_back"]),
            "testing": len([t for t in tasks if t.status == "testing"]),
        },
        "by_type": {
            "patch": len([t for t in tasks if t.type == "patch"]),
            "mock": len([t for t in tasks if t.type == "mock"]),
            "fallback": len([t for t in tasks if t.type == "fallback"]),
            "config": len([t for t in tasks if t.type == "config"]),
            "test": len([t for t in tasks if t.type == "test"]),
            "refactor": len([t for t in tasks if t.type == "refactor"]),
        },
        "tasks": [
            {
                "id": str(t.id),
                "title": t.title,
                "type": t.type,
                "status": t.status,
                "priority": t.priority,
                "files_count": len(t.files),
                "created_at": t.created_at.isoformat(),
                "applied_at": t.applied_at.isoformat() if t.applied_at else None,
            }
            for t in tasks
        ],
    }


@router.get("/{project_id}/testing")
async def get_testing_report(
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
    
    tests_result = await db.execute(
        select(TestExecution).where(TestExecution.project_id == project_id)
    )
    tests = tests_result.scalars().all()
    
    return {
        "project": {"id": str(project.id), "name": project.name},
        "total_executions": len(tests),
        "by_status": {
            "passed": len([t for t in tests if t.status == "passed"]),
            "failed": len([t for t in tests if t.status == "failed"]),
            "running": len([t for t in tests if t.status == "running"]),
            "pending": len([t for t in tests if t.status == "pending"]),
            "skipped": len([t for t in tests if t.status == "skipped"]),
        },
        "by_type": {
            "smoke": len([t for t in tests if t.type == "smoke"]),
            "happy_path": len([t for t in tests if t.type == "happy_path"]),
            "api": len([t for t in tests if t.type == "api"]),
            "ui": len([t for t in tests if t.type == "ui"]),
            "regression": len([t for t in tests if t.type == "regression"]),
            "environment": len([t for t in tests if t.type == "environment"]),
            "demo_readiness": len([t for t in tests if t.type == "demo_readiness"]),
        },
        "executions": [
            {
                "id": str(t.id),
                "type": t.type,
                "status": t.status,
                "passed": t.passed_count,
                "failed": t.failed_count,
                "skipped": t.skipped_count,
                "duration": t.total_duration,
                "started_at": t.started_at.isoformat(),
                "completed_at": t.completed_at.isoformat() if t.completed_at else None,
            }
            for t in tests
        ],
    }


@router.get("/{project_id}/demo-readiness")
async def get_demo_readiness_report(
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
    
    from app.models import RiskAssessment, Feature, DemoConfiguration, TestExecution
    
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
    
    demo_config_result = await db.execute(
        select(DemoConfiguration).where(DemoConfiguration.project_id == project_id)
    )
    demo_config = demo_config_result.scalar_one_or_none()
    
    latest_test_result = await db.execute(
        select(TestExecution)
        .where(TestExecution.project_id == project_id, TestExecution.type == "demo_readiness")
        .order_by(TestExecution.started_at.desc())
        .limit(1)
    )
    latest_test = latest_test_result.scalar_one_or_none()
    
    demo_path_features = [f for f in features if f.demo_path]
    stable_demo_features = [f for f in demo_path_features if f.status == "stable" and f.reliability_score >= 80]
    
    return {
        "project": {"id": str(project.id), "name": project.name},
        "demo_survival_score": project.demo_survival_score,
        "demo_readiness": project.demo_readiness,
        "critical_issues": project.critical_issues,
        "risk_level": risk.risk_level if risk else "unknown",
        "demo_features": {
            "total": len(demo_path_features),
            "stable": len(stable_demo_features),
            "unstable": len([f for f in demo_path_features if f.status in ["unstable", "critical"]]),
        },
        "demo_mode": {
            "configured": demo_config is not None,
            "enabled": demo_config.enabled if demo_config else False,
            "mock_data_count": len(demo_config.mock_data) if demo_config else 0,
            "api_fallbacks_count": len(demo_config.api_fallbacks) if demo_config else 0,
        },
        "latest_demo_test": {
            "status": latest_test.status if latest_test else "not_run",
            "passed": latest_test.passed_count if latest_test else 0,
            "failed": latest_test.failed_count if latest_test else 0,
        },
        "ready_for_demo": project.demo_readiness and project.demo_readiness >= 80,
    }


@router.get("/{project_id}/export")
async def export_report(
    project_id: UUID,
    type: str = Query(..., regex="^(scan|risk|stabilization|testing|demo-readiness|all)$"),
    format: str = Query("json", regex="^(json|markdown)$"),
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
    
    # This would call the individual report endpoints and combine them
    return {"message": f"Export {type} report in {format} format - not yet implemented"}