import asyncio
from uuid import UUID
from celery import shared_task
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, update
import structlog

from app.core.config import settings
from app.models import Project, RiskAssessment, Feature, FeatureDependency, RiskLevel, FeatureStatus, FeatureType

logger = structlog.get_logger()

engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def calculate_risk_score(feature, all_features, dependencies, scan_issues):
    score = 100
    factors = []
    
    feature_issues = [i for i in scan_issues if i["file"] in feature.path or feature.path in i["file"]]
    critical_issues = len([i for i in feature_issues if i["type"] == "error"])
    warning_issues = len([i for i in feature_issues if i["type"] == "warning"])
    
    if critical_issues > 0:
        score -= critical_issues * 15
        factors.append({"type": "critical_issues", "impact": critical_issues * 15, "description": f"{critical_issues} critical issues found", "evidence": f"Scan found {critical_issues} errors in related files"})
    if warning_issues > 0:
        score -= warning_issues * 5
        factors.append({"type": "warnings", "impact": warning_issues * 5, "description": f"{warning_issues} warnings found", "evidence": f"Scan found {warning_issues} warnings in related files"})
    
    dep_count = len(feature.dependencies) if feature.dependencies else 0
    if dep_count > 5:
        score -= (dep_count - 5) * 3
        factors.append({"type": "high_coupling", "impact": (dep_count - 5) * 3, "description": f"High dependency count ({dep_count})", "evidence": f"Feature depends on {dep_count} other components"})
    
    if feature.type == FeatureType.API:
        score -= 5
        factors.append({"type": "api_exposure", "impact": 5, "description": "API endpoints are inherently risky", "evidence": "External API calls can fail"})
    elif feature.type == FeatureType.INTEGRATION:
        score -= 10
        factors.append({"type": "external_dependency", "impact": 10, "description": "External integrations add risk", "evidence": "Third-party services may be unavailable"})
    
    return max(0, score), factors


def predict_failures(features, risk_scores):
    predictions = []
    for feature in features:
        score = next((r["score"] for r in risk_scores if r["feature_id"] == str(feature.id)), 100)
        if score < 50:
            predictions.append({
                "id": f"pred-{feature.id}",
                "feature_id": str(feature.id),
                "feature_name": feature.name,
                "probability": (100 - score) / 100,
                "impact": "critical" if score < 30 else "high" if score < 50 else "medium",
                "description": f"Feature '{feature.name}' has low reliability score ({score})",
                "mitigations": ["Add mock data", "Implement fallback", "Increase test coverage"],
                "is_estimate": True,
            })
    return predictions


def find_happy_paths(features, risk_scores):
    happy_paths = []
    
    demo_features = [f for f in features if f.demo_path]
    if demo_features:
        avg_reliability = sum(next((r["score"] for r in risk_scores if r["feature_id"] == str(f.id)), 100) for f in demo_features) / len(demo_features)
        happy_paths.append({
            "id": "happy-path-main",
            "name": "Main Demo Flow",
            "description": "Core user journey through demo features",
            "features": [str(f.id) for f in demo_features],
            "reliability": avg_reliability,
            "steps": [
                {"feature_id": str(f.id), "feature_name": f.name, "action": f"Demonstrate {f.name}", "expected_result": "Works correctly"}
                for f in demo_features
            ],
            "estimated_duration": len(demo_features) * 2,
        })
    
    return happy_paths


def assess_dependency_risks(dependencies, features):
    risks = []
    feature_map = {str(f.id): f for f in features}
    
    for dep in dependencies:
        if dep.get("status") == "outdated":
            risks.append({
                "dependency": dep["name"],
                "risk_level": "medium",
                "reason": f"Outdated dependency: {dep.get('version', 'unknown')}",
                "affected_features": [],
            })
        elif dep.get("status") == "vulnerable":
            risks.append({
                "dependency": dep["name"],
                "risk_level": "high",
                "reason": f"Known vulnerability in {dep.get('version', 'unknown')}",
                "affected_features": [],
            })
    
    return risks


def generate_ai_recommendations(features, risk_scores, predictions, dependencies):
    recommendations = []
    
    for pred in predictions:
        if pred["probability"] > 0.5:
            recommendations.append({
                "id": f"rec-{pred['feature_id']}",
                "type": "stabilization",
                "priority": pred["impact"],
                "title": f"Stabilize {pred['feature_name']}",
                "description": f"Feature has {pred['probability']*100:.0f}% failure probability",
                "affected_files": [pred["feature_id"]],
                "estimated_effort": "medium",
                "expected_impact": "Reduce failure probability by 50%",
                "confidence": 0.8,
                "is_estimate": True,
            })
    
    critical_features = [r for r in risk_scores if r["score"] < 40]
    for feat in critical_features:
        recommendations.append({
            "id": f"rec-mock-{feat['feature_id']}",
            "type": "mock",
            "priority": "high",
            "title": f"Add mock data for {feat['feature_name']}",
            "description": "Create deterministic mock data to replace unreliable external dependencies",
            "affected_files": [feat["feature_id"]],
            "estimated_effort": "low",
            "expected_impact": "Eliminate external dependency failures",
            "confidence": 0.9,
            "is_estimate": True,
        })
    
    return recommendations


@shared_task(bind=True, max_retries=3)
def analyze_project_task(self, project_id: str):
    async def _analyze():
        project_uuid = UUID(project_id)
        
        async with async_session_maker() as db:
            result = await db.execute(select(Project).where(Project.id == project_uuid))
            project = result.scalar_one_or_none()
            if not project:
                return
            
            features_result = await db.execute(select(Feature).where(Feature.project_id == project_uuid))
            features = features_result.scalars().all()
            
            deps_result = await db.execute(select(FeatureDependency).where(FeatureDependency.project_id == project_uuid))
            dependencies = deps_result.scalars().all()
            
            scan_result = await db.execute(
                select(Project).where(Project.id == project_uuid)
            )
            # Get latest scan issues from scan session
            from app.models import ScanSession, ScanFinding
            scan_sessions = await db.execute(
                select(ScanSession).where(ScanSession.project_id == project_uuid).order_by(ScanSession.started_at.desc()).limit(1)
            )
            latest_scan = scan_sessions.scalar_one_or_none()
            scan_issues = []
            if latest_scan:
                findings = await db.execute(select(ScanFinding).where(ScanFinding.scan_session_id == latest_scan.id))
                scan_issues = [
                    {"type": f.type, "category": f.category, "file": f.file, "line": f.line, "message": f.message}
                    for f in findings.scalars().all()
                ]
        
        risk_scores = []
        for feature in features:
            score, factors = calculate_risk_score(feature, features, dependencies, scan_issues)
            risk_level = RiskLevel.CRITICAL if score < 30 else RiskLevel.HIGH if score < 50 else RiskLevel.MEDIUM if score < 70 else RiskLevel.LOW
            
            risk_scores.append({
                "feature_id": str(feature.id),
                "feature_name": feature.name,
                "score": score,
                "risk_level": risk_level.value,
                "factors": factors,
                "demo_value": 10 if feature.demo_path else 5,
            })
        
        predictions = predict_failures(features, risk_scores)
        happy_paths = find_happy_paths(features, risk_scores)
        dependency_risks = assess_dependency_risks(
            [{"name": d.name, "status": "up-to-date"} for d in dependencies],
            features
        )
        recommendations = generate_ai_recommendations(features, risk_scores, predictions, dependencies)
        
        overall_score = sum(r["score"] for r in risk_scores) // len(risk_scores) if risk_scores else 100
        overall_risk = RiskLevel.CRITICAL if overall_score < 30 else RiskLevel.HIGH if overall_score < 50 else RiskLevel.MEDIUM if overall_score < 70 else RiskLevel.LOW
        
        risk_distribution = {
            "critical": len([r for r in risk_scores if r["risk_level"] == "critical"]),
            "high": len([r for r in risk_scores if r["risk_level"] == "high"]),
            "medium": len([r for r in risk_scores if r["risk_level"] == "medium"]),
            "low": len([r for r in risk_scores if r["risk_level"] == "low"]),
        }
        
        async with async_session_maker() as db:
            assessment = RiskAssessment(
                project_id=project_uuid,
                overall_score=overall_score,
                risk_level=overall_risk,
                risk_distribution=risk_distribution,
                feature_scores=risk_scores,
                failure_predictions=predictions,
                happy_paths=happy_paths,
                dependency_risks=dependency_risks,
                ai_recommendations=recommendations,
            )
            db.add(assessment)
            
            project.demo_survival_score = overall_score
            project.feature_reliability = overall_score / 100.0
            project.critical_issues = risk_distribution["critical"] + risk_distribution["high"]
            await db.commit()
        
        logger.info("Analysis completed", project_id=project_id, score=overall_score)
    
    try:
        asyncio.run(_analyze())
    except Exception as e:
        logger.error("Analysis failed", project_id=project_id, error=str(e))
        raise