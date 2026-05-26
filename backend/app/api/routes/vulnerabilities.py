"""Vulnerability routes."""

from datetime import datetime, timezone
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_permission
from app.core.rbac import Permission
from app.db.session import get_db
from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.vulnerability_repository import VulnerabilityRepository
from app.schemas.vulnerability import (
    SuppressRequest,
    VulnerabilityListResponse,
    VulnerabilityResponse,
)

router = APIRouter()


@router.get("", response_model=VulnerabilityListResponse)
async def list_vulnerabilities(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission(Permission.VIEW_VULNERABILITIES))],
    repository_id: Optional[UUID] = None,
    severity: Optional[str] = None,
    tool: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    repo = VulnerabilityRepository(db)
    items, total = await repo.list_filtered(repository_id, severity, tool, skip, limit)
    return VulnerabilityListResponse(items=items, total=total)


@router.get("/{vuln_id}", response_model=VulnerabilityResponse)
async def get_vulnerability(
    vuln_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission(Permission.VIEW_VULNERABILITIES))],
):
    repo = VulnerabilityRepository(db)
    vuln = await repo.get_by_id(vuln_id)
    if not vuln:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return vuln


@router.post("/{vuln_id}/suppress", response_model=VulnerabilityResponse)
async def suppress_vulnerability(
    vuln_id: UUID,
    data: SuppressRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission(Permission.SUPPRESS_VULNERABILITIES))],
):
    repo = VulnerabilityRepository(db)
    audit = AuditRepository(db)
    vuln = await repo.get_by_id(vuln_id)
    if not vuln:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    vuln.is_suppressed = True
    vuln.suppressed_at = datetime.now(timezone.utc)
    vuln.suppressed_by = user.id
    await audit.log("vulnerability.suppress", "vulnerability", str(vuln_id), user.id, details={"reason": data.reason})
    await db.flush()
    return vuln
