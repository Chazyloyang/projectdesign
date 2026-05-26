"""Celery background tasks."""

import asyncio
import logging
from uuid import UUID

from app.core.metrics import ACTIVE_PIPELINES, PIPELINE_RUNS
from app.db.session import AsyncSessionLocal
from app.services.scan_service import ScanService
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


async def _run_pipeline_async(pipeline_id: str) -> None:
    async with AsyncSessionLocal() as session:
        try:
            service = ScanService(session)
            await service.execute_pipeline(UUID(pipeline_id))
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@celery_app.task(name="run_pipeline", bind=True, max_retries=2)
def run_pipeline_task(self, pipeline_id: str) -> dict:
    try:
        asyncio.run(_run_pipeline_async(pipeline_id))
        PIPELINE_RUNS.labels(status="completed", repository_id="unknown").inc()
        return {"status": "completed", "pipeline_id": pipeline_id}
    except Exception as exc:
        logger.exception("Pipeline task failed: %s", exc)
        raise self.retry(exc=exc, countdown=30)
    finally:
        ACTIVE_PIPELINES.dec()
