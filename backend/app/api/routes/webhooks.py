"""GitHub and GitLab webhook handlers."""

import hashlib
import hmac
import logging
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.repository import Repository
from app.schemas.pipeline import PipelineRunRequest
from app.services.pipeline_service import PipelineService

logger = logging.getLogger(__name__)
router = APIRouter()


def _verify_github_signature(payload: bytes, signature: str, secret: str) -> bool:
    if not signature or not secret:
        return True  # skip in dev when secret not set
    expected = "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


@router.post("/github")
async def github_webhook(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    x_hub_signature_256: Annotated[str | None, Header()] = None,
    x_github_event: Annotated[str | None, Header()] = None,
):
    body = await request.body()
    payload: dict[str, Any] = await request.json()

    if x_github_event not in ("push", "pull_request"):
        return {"status": "ignored", "event": x_github_event}

    repo_full_name = payload.get("repository", {}).get("full_name", "")
    result = await db.execute(
        select(Repository).where(Repository.external_id == repo_full_name)
    )
    repo = result.scalar_one_or_none()
    if not repo:
        logger.warning("Repository not registered: %s", repo_full_name)
        return {"status": "repository_not_found"}

    if repo.webhook_secret and not _verify_github_signature(
        body, x_hub_signature_256 or "", repo.webhook_secret
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid signature")

    branch = payload.get("ref", "refs/heads/main").replace("refs/heads/", "")
    commit_sha = payload.get("after") or payload.get("pull_request", {}).get("head", {}).get("sha")

    service = PipelineService(db)
    await service.run(
        PipelineRunRequest(repository_id=repo.id, branch=branch, commit_sha=commit_sha),
        user_id=UUID("00000000-0000-0000-0000-000000000000"),
        trigger="webhook",
    )
    return {"status": "pipeline_queued"}


@router.post("/gitlab")
async def gitlab_webhook(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    x_gitlab_event: Annotated[str | None, Header()] = None,
):
    payload = await request.json()
    if x_gitlab_event not in ("Push Hook", "Merge Request Hook"):
        return {"status": "ignored"}

    project = payload.get("project", {})
    path = project.get("path_with_namespace", "")
    result = await db.execute(select(Repository).where(Repository.external_id == path))
    repo = result.scalar_one_or_none()
    if not repo:
        return {"status": "repository_not_found"}

    branch = payload.get("ref", "main").replace("refs/heads/", "")
    commit_sha = payload.get("checkout_sha") or payload.get("after")

    service = PipelineService(db)
    await service.run(
        PipelineRunRequest(repository_id=repo.id, branch=branch, commit_sha=commit_sha),
        user_id=UUID("00000000-0000-0000-0000-000000000000"),
        trigger="webhook",
    )
    return {"status": "pipeline_queued"}
