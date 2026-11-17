import asyncio
from uuid import UUID
from celery import shared_task
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, update
import structlog

from app.core.config import settings
from app.models import Project, StabilizationTask, Patch, TaskStatus

logger = structlog.get_logger()

engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@shared_task(bind=True, max_retries=3)
def apply_patches_task(self, task_id: str):
    async def _apply():
        task_uuid = UUID(task_id)
        
        async with async_session_maker() as db:
            result = await db.execute(select(StabilizationTask).where(StabilizationTask.id == task_uuid))
            task = result.scalar_one_or_none()
            if not task:
                return
            
            task.status = TaskStatus.TESTING
            await db.commit()
            
            if not task.project.storage_path:
                task.status = TaskStatus.REJECTED
                await db.commit()
                return
            
            project_path = Path(task.project.storage_path)
            
            for patch_data in task.files:
                if not patch_data.get("approved", False):
                    continue
                
                file_path = project_path / patch_data["path"]
                if not file_path.exists():
                    continue
                
                backup_path = file_path.with_suffix(file_path.suffix + ".backup")
                shutil.copy2(file_path, backup_path)
                
                file_path.write_text(patch_data["proposed_content"], encoding="utf-8")
                
                patch = Patch(
                    task_id=task.id,
                    file_path=patch_data["path"],
                    original_content=patch_data["original_content"],
                    modified_content=patch_data["proposed_content"],
                    diff=patch_data["diff"],
                    status="applied",
                )
                db.add(patch)
            
            task.status = TaskStatus.APPLIED
            task.applied_at = datetime.utcnow()
            await db.commit()
        
        logger.info("Patches applied", task_id=task_id)
    
    try:
        import shutil
        from pathlib import Path
        from datetime import datetime
        asyncio.run(_apply())
    except Exception as e:
        logger.error("Patch application failed", task_id=task_id, error=str(e))
        raise