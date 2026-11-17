from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID

from app.core.security import get_current_active_user
from app.db.session import get_db
from app.models import User, Team, TeamMember, Project, RiskAssessment, Feature, FeatureDependency
from app.schemas import (
    RiskAssessmentResponse, FeatureRiskScore, FailurePrediction, HappyPath, DependencyRisk, AIRecommendation,
    FeatureResponse, FeatureUpdate,
)
from app.workers.celery_app import analyze_project_task

router = APIRouter()


@router.post("/{project_id}/analyze")
async def analyze_project(
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
    
    analyze_project_task.delay(str(project_id))
    return {"message": "Analysis started"}


@router.get("/{project_id}/assessment", response_model=RiskAssessmentResponse)
async def get_risk_assessment(
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
        raise HTTPException(status_code=404, detail="No risk assessment found. Run analysis first.")
    
    return risk


@router.get("/{project_id}/feature-graph")
async def get_feature_graph(
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
    
    features_result = await db.execute(
        select(Feature).where(Feature.project_id == project_id)
    )
    features = features_result.scalars().all()
    
    deps_result = await db.execute(
        select(FeatureDependency).where(FeatureDependency.project_id == project_id)
    )
    dependencies = deps_result.scalars().all()
    
    nodes = [
        {
            "id": str(f.id),
            "label": f.name,
            "type": f.type,
            "status": f.status,
            "reliability": f.reliability_score,
            "demo_path": f.demo_path,
        }
        for f in features
    ]
    
    edges = [
        {
            "source": str(d.source_feature_id),
            "target": str(d.target_feature_id),
            "type": d.type,
            "strength": d.strength,
        }
        for d in dependencies
    ]
    
    return {"nodes": nodes, "edges": edges}


@router.get("/{project_id}/happy-paths")
async def get_happy_paths(
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
    
    return {"happy_paths": risk.happy_paths}


@router.get("/{project_id}/recommendations")
async def get_recommendations(
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
    
    return {"recommendations": risk.ai_recommendations}