import asyncio
from uuid import UUID
from celery import shared_task
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select
from datetime import datetime
import structlog

from app.core.config import settings
from app.models import Project, DemoScript, Feature, FeatureStatus, RiskAssessment

logger = structlog.get_logger()

engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def generate_script_sections(project, features, risk_assessment, duration_minutes, audience):
    sections = []
    
    time_per_section = duration_minutes / 8
    
    sections.append({
        "id": f"section-{datetime.utcnow().timestamp()}-intro",
        "type": "intro",
        "title": "Introduction",
        "content": f"Welcome! I'm presenting {project.name}, a project that solves [problem]. In the next {duration_minutes} minutes, I'll show you how it works.",
        "duration_minutes": max(1, int(time_per_section)),
        "features": [],
        "talking_points": [
            "Hook the audience with the problem",
            "Briefly introduce the solution",
            "Set expectations for the demo",
        ],
        "backup_content": "If time is short, skip to the main demo.",
    })
    
    sections.append({
        "id": f"section-{datetime.utcnow().timestamp()}-problem",
        "type": "problem",
        "title": "The Problem",
        "content": "The problem we're solving is... [describe the pain point your project addresses]",
        "duration_minutes": max(1, int(time_per_section)),
        "features": [],
        "talking_points": [
            "Describe the pain point clearly",
            "Use a relatable example",
            "Quantify the impact if possible",
        ],
        "backup_content": "Problem statement is critical - don't skip.",
    })
    
    sections.append({
        "id": f"section-{datetime.utcnow().timestamp()}-overview",
        "type": "overview",
        "title": "Project Overview",
        "content": f"{project.name} is a [type of application] built with [tech stack]. It provides [key value proposition].",
        "duration_minutes": max(1, int(time_per_section)),
        "features": [],
        "talking_points": [
            "High-level architecture",
            "Key technologies used",
            "Unique approach or innovation",
        ],
    })
    
    demo_features = [f for f in features if f.demo_path and f.status == FeatureStatus.STABLE]
    if not demo_features:
        demo_features = [f for f in features if f.status == FeatureStatus.STABLE][:5]
    
    for i, feature in enumerate(demo_features):
        sections.append({
            "id": f"section-{datetime.utcnow().timestamp()}-demo-{i}",
            "type": "demo",
            "title": f"Demo: {feature.name}",
            "content": f"Now let me show you {feature.name}. This feature allows users to [describe what it does].",
            "duration_minutes": max(1, int(time_per_section)),
            "features": [str(feature.id)],
            "talking_points": [
                f"Show {feature.name} in action",
                "Explain the user benefit",
                "Highlight any technical innovation",
            ],
            "backup_content": f"If {feature.name} fails, show screenshots or pre-recorded video.",
        })
    
    sections.append({
        "id": f"section-{datetime.utcnow().timestamp()}-architecture",
        "type": "architecture",
        "title": "Technical Architecture",
        "content": "Under the hood, the system uses [architecture pattern]. Key components include...",
        "duration_minutes": max(1, int(time_per_section)),
        "features": [],
        "talking_points": [
            "Architecture diagram walkthrough",
            "Data flow explanation",
            "Scalability considerations",
        ],
    })
    
    sections.append({
        "id": f"section-{datetime.utcnow().timestamp()}-results",
        "type": "results",
        "title": "Results & Impact",
        "content": f"With {project.name}, we achieved [metrics]. This translates to [business impact].",
        "duration_minutes": max(1, int(time_per_section)),
        "features": [],
        "talking_points": [
            "Quantify results with metrics",
            "Share user feedback if available",
            "Compare to alternatives",
        ],
    })
    
    sections.append({
        "id": f"section-{datetime.utcnow().timestamp()}-conclusion",
        "type": "conclusion",
        "title": "Conclusion",
        "content": f"In summary, {project.name} solves [problem] by [solution]. We're excited about [future plans]. Thank you!",
        "duration_minutes": max(1, int(time_per_section)),
        "features": [],
        "talking_points": [
            "Recap the problem and solution",
            "Call to action",
            "Thank the audience",
        ],
    })
    
    qa_questions = [
        "What was the biggest technical challenge?",
        "How does this scale?",
        "What's your go-to-market strategy?",
        "How do you handle [edge case]?",
        "What would you do with more time?",
    ]
    
    if risk_assessment:
        for pred in risk_assessment.failure_predictions[:3]:
            qa_questions.append(f"How do you handle potential failures in {pred['feature_name']}?")
    
    sections.append({
        "id": f"section-{datetime.utcnow().timestamp()}-qa",
        "type": "qa",
        "title": "Q&A Preparation",
        "content": "Anticipated judge questions and suggested answers.",
        "duration_minutes": max(1, int(time_per_section)),
        "features": [],
        "talking_points": qa_questions,
        "backup_content": "Prepare honest answers about limitations.",
    })
    
    return sections


@shared_task(bind=True, max_retries=3)
def generate_demo_script_task(self, script_id: str):
    async def _generate():
        script_uuid = UUID(script_id)
        
        async with async_session_maker() as db:
            result = await db.execute(select(DemoScript).where(DemoScript.id == script_uuid))
            script = result.scalar_one_or_none()
            if not script:
                return
            
            project_result = await db.execute(select(Project).where(Project.id == script.project_id))
            project = project_result.scalar_one_or_none()
            if not project:
                return
            
            features_result = await db.execute(
                select(Feature)
                .where(Feature.project_id == project.id)
                .order_by(Feature.reliability_score.desc())
            )
            features = features_result.scalars().all()
            
            risk_result = await db.execute(
                select(RiskAssessment)
                .where(RiskAssessment.project_id == project.id)
                .order_by(RiskAssessment.created_at.desc())
                .limit(1)
            )
            risk = risk_result.scalar_one_or_none()
            
            if script.verified_features_only:
                features = [f for f in features if f.status == FeatureStatus.STABLE and f.reliability_score >= 70]
            
            sections = generate_script_sections(project, features, risk, script.duration_minutes, script.audience)
            
            script.sections = sections
            script.updated_at = datetime.utcnow()
            await db.commit()
        
        logger.info("Demo script generated", script_id=script_id)
    
    try:
        asyncio.run(_generate())
    except Exception as e:
        logger.error("Demo script generation failed", script_id=script_id, error=str(e))
        raise