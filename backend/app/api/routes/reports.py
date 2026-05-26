"""Report export routes."""

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_permission
from app.core.rbac import Permission
from app.db.session import get_db
from app.models.user import User
from app.services.report_service import ReportService

router = APIRouter()


@router.get("/security/pdf")
async def export_security_pdf(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission(Permission.EXPORT_REPORTS))],
):
    service = ReportService(db)
    content = await service.build_security_pdf()
    return Response(
        content=content,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="security-report.pdf"'},
    )


@router.get("/security/csv")
async def export_security_csv(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission(Permission.EXPORT_REPORTS))],
):
    service = ReportService(db)
    content = await service.build_security_csv()
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="security-report.csv"'},
    )


@router.get("/quality/csv")
async def export_quality_csv(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission(Permission.EXPORT_REPORTS))],
):
    service = ReportService(db)
    content = await service.build_quality_csv()
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="quality-metrics.csv"'},
    )


@router.get("/quality/pdf")
async def export_quality_pdf(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission(Permission.EXPORT_REPORTS))],
):
    service = ReportService(db)
    content = await service.build_quality_pdf()
    return Response(
        content=content,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="quality-report.pdf"'},
    )
