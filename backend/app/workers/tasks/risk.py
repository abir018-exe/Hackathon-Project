import asyncio
from uuid import UUID
from celery import shared_task
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, update
from datetime import datetime
import structlog
import subprocess

from app.core.config import settings
from app.models import Project, GitCommit, RiskLevel, Feature

logger = structlog.get_logger()

engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


DEMO_CRITICAL_PATHS = [
    "api", "auth", "payment", "checkout", "login", "signup",
    "dashboard", "main", "core", "service", "model",
]


def analyze_commit_risk(project_path: Path, sha: str, features: list) -> dict:
    try:
        result = subprocess.run(
            ["git", "show", "--name-only", "--pretty=format:", sha],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=30
        )
        files_changed = [f.strip() for f in result.stdout.splitlines() if f.strip()]
    except Exception:
        files_changed = []
    
    try:
        result = subprocess.run(
            ["git", "show", "--stat", "--pretty=format:", sha],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=30
        )
        stat_lines = result.stdout.splitlines()
        additions = 0
        deletions = 0
        for line in stat_lines:
            if "insertion" in line or "deletion" in line:
                parts = line.split(",")
                for part in parts:
                    part = part.strip()
                    if "insertion" in part:
                        additions += int(part.split()[0])
                    elif "deletion" in part:
                        deletions += int(part.split()[0])
    except Exception:
        additions = 0
        deletions = 0
    
    risk_level = RiskLevel.LOW
    risk_reason = None
    affects_demo_path = False
    
    for file_path in files_changed:
        for critical_path in DEMO_CRITICAL_PATHS:
            if critical_path in file_path.lower():
                affects_demo_path = True
                risk_level = RiskLevel.HIGH
                risk_reason = f"Changes to critical path: {critical_path}"
                break
        
        if file_path.endswith((".py", ".js", ".ts", ".jsx", ".tsx")):
            if "test" not in file_path.lower() and "spec" not in file_path.lower():
                if additions + deletions > 100:
                    risk_level = max(risk_level, RiskLevel.MEDIUM, key=lambda x: ["low", "medium", "high", "critical"].index(x.value))
                    risk_reason = f"Large changes to source file ({additions + deletions} lines)"
        
        if any(keyword in file_path.lower() for keyword in ["config", "env", "secret", "key", "credential"]):
            risk_level = max(risk_level, RiskLevel.HIGH, key=lambda x: ["low", "medium", "high", "critical"].index(x.value))
            risk_reason = f"Configuration or security-related file modified"
    
    if additions + deletions > 500:
        risk_level = RiskLevel.CRITICAL
        risk_reason = "Very large commit (>500 lines changed)"
    
    file_changes = []
    for file_path in files_changed:
        status = "modified"
        if "new file" in file_path:
            status = "added"
        elif "deleted" in file_path:
            status = "deleted"
        file_changes.append({
            "path": file_path,
            "status": status,
            "additions": additions // max(len(files_changed), 1),
            "deletions": deletions // max(len(files_changed), 1),
        })
    
    return {
        "files_changed": file_changes,
        "risk_level": risk_level,
        "risk_reason": risk_reason,
        "affects_demo_path": affects_demo_path,
    }


@shared_task(bind=True, max_retries=3)
def analyze_commit_task(self, project_id: str, sha: str):
    async def _analyze():
        project_uuid = UUID(project_id)
        
        async with async_session_maker() as db:
            result = await db.execute(select(Project).where(Project.id == project_uuid))
            project = result.scalar_one_or_none()
            if not project or not project.storage_path:
                return
            
            features_result = await db.execute(select(Feature).where(Feature.project_id == project_uuid))
            features = features_result.scalars().all()
            
            existing = await db.execute(
                select(GitCommit).where(GitCommit.project_id == project_uuid, GitCommit.sha == sha)
            )
            if existing.scalar_one_or_none():
                return
            
            try:
                result = subprocess.run(
                    ["git", "show", "-s", "--format=%an|%ae|%ci|%s", sha],
                    cwd=project.storage_path,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode != 0:
                    return
                
                parts = result.stdout.strip().split("|", 3)
                if len(parts) < 4:
                    return
                
                author, author_email, timestamp_str, message = parts
                timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            except Exception:
                return
            
            analysis = analyze_commit_risk(Path(project.storage_path), sha, features)
            
            commit = GitCommit(
                project_id=project_uuid,
                sha=sha,
                message=message,
                author=author,
                author_email=author_email,
                timestamp=timestamp,
                files_changed=analysis["files_changed"],
                risk_level=analysis["risk_level"],
                risk_reason=analysis["risk_reason"],
                affects_demo_path=analysis["affects_demo_path"],
            )
            db.add(commit)
            
            if analysis["affects_demo_path"] and analysis["risk_level"] in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                from app.models import Notification, NotificationType
                notification = Notification(
                    user_id=project.team.owner_id,
                    type=NotificationType.WARNING,
                    title=f"Risky commit detected: {sha[:8]}",
                    message=f"Commit {sha[:8]} modifies demo-critical paths with {analysis['risk_level'].value} risk: {analysis['risk_reason']}",
                    action_url=f"/risk-monitor/{project_id}",
                )
                db.add(notification)
            
            await db.commit()
        
        logger.info("Commit analyzed", project_id=project_id, sha=sha[:8], risk=analysis["risk_level"].value)
    
    try:
        asyncio.run(_analyze())
    except Exception as e:
        logger.error("Commit analysis failed", project_id=project_id, sha=sha, error=str(e))
        raise