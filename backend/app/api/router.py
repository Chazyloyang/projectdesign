"""API router aggregation."""

from fastapi import APIRouter

from app.api.routes import analytics, auth, health, pipelines, reports, repositories, vulnerabilities, webhooks

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(repositories.router, prefix="/repositories", tags=["repositories"])
api_router.include_router(pipelines.router, prefix="/pipelines", tags=["pipelines"])
api_router.include_router(vulnerabilities.router, prefix="/vulnerabilities", tags=["vulnerabilities"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
