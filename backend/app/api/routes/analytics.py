"""Analytics routes."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_permission
from app.core.rbac import Permission
from app.db.session import get_db
from app.models.user import User
from app.schemas.analytics import AnalyticsResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/dashboard", response_model=AnalyticsResponse)
async def dashboard(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission(Permission.VIEW_ANALYTICS))],
):
    service = AnalyticsService(db)
    return await service.get_dashboard()
