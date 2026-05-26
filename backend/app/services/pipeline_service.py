"""Pipeline orchestration service."""

from datetime import datetime, timezone
from typing import List
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.metrics import ACTIVE_PIPELINES, PIPELINE_RUNS
from app.models.pipeline import Pipeline, PipelineStage
from app.repositories.audit_repository import AuditRepository
from app.repositories.pipeline_repository import PipelineRepository
from app.repositories.repository_repository import RepositoryRepository
from app.schemas.pipeline import PipelineRunRequest

PIPELINE_STAGES = [
    "checkout",
    "dependencies",
    "lint",
    "sast",
    "test",
    "coverage",
    "sonarqube",
    "quality_gate",
    "report",
]


class PipelineService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.pipelines = PipelineRepository(session)
        self.repos = RepositoryRepository(session)
        self.audit = AuditRepository(session)

    async def run(self, data: PipelineRunRequest, user_id: UUID, trigger: str = "manual") -> Pipeline:
        repo = await self.repos.get_by_id(data.repository_id)
        if not repo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")

        stages = [
            PipelineStage(name=name, status="pending", order=i)
            for i, name in enumerate(PIPELINE_STAGES)
        ]
        pipeline = Pipeline(
            repository_id=data.repository_id,
            status="queued",
            branch=data.branch,
            commit_sha=data.commit_sha,
            trigger=trigger,
            started_at=datetime.now(timezone.utc),
        )
        created = await self.pipelines.create(pipeline, stages)
        pipeline_id = created.id
        await self.audit.log("pipeline.start", "pipeline", str(pipeline_id), user_id)
        # Commit before Celery picks up the task (avoid race with get_db commit at end of request)
        await self.session.commit()

        from app.workers.tasks import run_pipeline_task

        run_pipeline_task.delay(str(pipeline_id))
        ACTIVE_PIPELINES.inc()
        PIPELINE_RUNS.labels(status="queued", repository_id=str(data.repository_id)).inc()
        # Re-load after commit so Pydantic can read stages without async lazy-load
        reloaded = await self.pipelines.get_by_id(pipeline_id)
        if not reloaded:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Pipeline not found")
        return reloaded

    async def get(self, pipeline_id: UUID) -> Pipeline:
        pipeline = await self.pipelines.get_by_id(pipeline_id)
        if not pipeline:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pipeline not found")
        return pipeline

    async def list(self, repository_id: UUID, skip: int = 0, limit: int = 20):
        return await self.pipelines.list_by_repository(repository_id, skip, limit)
