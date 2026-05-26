"""Pipeline data access."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.pipeline import Pipeline, PipelineStage


class PipelineRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, pipeline_id: UUID) -> Optional[Pipeline]:
        result = await self.session.execute(
            select(Pipeline)
            .options(selectinload(Pipeline.stages))
            .where(Pipeline.id == pipeline_id)
        )
        return result.scalar_one_or_none()

    async def list_by_repository(
        self, repository_id: UUID, skip: int = 0, limit: int = 20
    ) -> tuple[List[Pipeline], int]:
        base = select(Pipeline).where(Pipeline.repository_id == repository_id)
        count_q = select(func.count()).select_from(Pipeline).where(
            Pipeline.repository_id == repository_id
        )
        total = (await self.session.execute(count_q)).scalar() or 0
        result = await self.session.execute(
            base.options(selectinload(Pipeline.stages))
            .order_by(Pipeline.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all()), total

    async def create(self, pipeline: Pipeline, stages: List[PipelineStage]) -> Pipeline:
        pipeline.stages = stages
        self.session.add(pipeline)
        await self.session.flush()
        # Eager-load stages for async-safe serialization (avoids MissingGreenlet on response)
        result = await self.session.execute(
            select(Pipeline)
            .options(selectinload(Pipeline.stages))
            .where(Pipeline.id == pipeline.id)
        )
        return result.scalar_one()

    async def update(self, pipeline: Pipeline) -> Pipeline:
        await self.session.flush()
        await self.session.refresh(pipeline)
        return pipeline

    async def count_by_status(self, status: str) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(Pipeline).where(Pipeline.status == status)
        )
        return result.scalar() or 0
