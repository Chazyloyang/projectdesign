"""Pipeline routes."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_permission
from app.core.rbac import Permission
from app.db.session import get_db
from app.models.user import User
from app.schemas.pipeline import PipelineListResponse, PipelineResponse, PipelineRunRequest
from app.services.pipeline_service import PipelineService

router = APIRouter()


@router.post("/run", response_model=PipelineResponse)
async def run_pipeline(
    data: PipelineRunRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission(Permission.RUN_PIPELINES))],
):
    service = PipelineService(db)
    return await service.run(data, user.id)


@router.get("/{pipeline_id}", response_model=PipelineResponse)
async def get_pipeline(
    pipeline_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    service = PipelineService(db)
    return await service.get(pipeline_id)


@router.get("", response_model=PipelineListResponse)
async def list_pipelines(
    repository_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    service = PipelineService(db)
    items, total = await service.list(repository_id, skip, limit)
    return PipelineListResponse(items=items, total=total)
