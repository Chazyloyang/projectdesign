"""Repository routes."""

from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_permission
from app.core.rbac import Permission
from app.db.session import get_db
from app.models.user import User
from app.schemas.repository import RepositoryCreate, RepositoryListResponse, RepositoryResponse
from app.services.repository_service import RepositoryService

router = APIRouter()


@router.post("", response_model=RepositoryResponse)
async def create_repository(
    data: RepositoryCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission(Permission.CONNECT_REPOS))],
):
    service = RepositoryService(db)
    return await service.create(data, user.id)


@router.get("", response_model=RepositoryListResponse)
async def list_repositories(
    organization_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    service = RepositoryService(db)
    items, total = await service.list(organization_id, skip, limit)
    return RepositoryListResponse(items=items, total=total)


@router.delete("/{repo_id}")
async def delete_repository(
    repo_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission(Permission.CONNECT_REPOS))],
):
    service = RepositoryService(db)
    await service.delete(repo_id, user.id)
    return {"status": "deleted"}
