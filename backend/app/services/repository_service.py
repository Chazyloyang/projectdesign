"""Repository management service."""

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import encrypt_secret
from app.models.repository import Repository
from app.repositories.audit_repository import AuditRepository
from app.repositories.repository_repository import RepositoryRepository
from app.schemas.repository import RepositoryCreate


class RepositoryService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repos = RepositoryRepository(session)
        self.audit = AuditRepository(session)

    async def create(self, data: RepositoryCreate, user_id: UUID) -> Repository:
        repo = Repository(
            organization_id=data.organization_id,
            name=data.name,
            provider=data.provider,
            url=data.url,
            external_id=data.external_id,
            default_branch=data.default_branch,
            access_token_encrypted=encrypt_secret(data.access_token) if data.access_token else None,
        )
        created = await self.repos.create(repo)
        await self.audit.log("repository.create", "repository", str(created.id), user_id)
        return created

    async def list(self, organization_id: UUID, skip: int = 0, limit: int = 50):
        return await self.repos.list_by_org(organization_id, skip, limit)

    async def delete(self, repo_id: UUID, user_id: UUID) -> None:
        repo = await self.repos.get_by_id(repo_id)
        if not repo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")
        await self.repos.delete(repo)
        await self.audit.log("repository.delete", "repository", str(repo_id), user_id)
