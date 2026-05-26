"""Repository data access."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.repository import Repository


class RepositoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, repo_id: UUID) -> Optional[Repository]:
        result = await self.session.execute(select(Repository).where(Repository.id == repo_id))
        return result.scalar_one_or_none()

    async def list_by_org(
        self, organization_id: UUID, skip: int = 0, limit: int = 50
    ) -> tuple[List[Repository], int]:
        query = select(Repository).where(Repository.organization_id == organization_id)
        count_q = select(func.count()).select_from(Repository).where(
            Repository.organization_id == organization_id
        )
        total = (await self.session.execute(count_q)).scalar() or 0
        result = await self.session.execute(query.offset(skip).limit(limit))
        return list(result.scalars().all()), total

    async def create(self, repo: Repository) -> Repository:
        self.session.add(repo)
        await self.session.flush()
        await self.session.refresh(repo)
        return repo

    async def delete(self, repo: Repository) -> None:
        await self.session.delete(repo)

    async def count_all(self) -> int:
        result = await self.session.execute(select(func.count()).select_from(Repository))
        return result.scalar() or 0
