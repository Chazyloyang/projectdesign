"""Analytics and KPI service."""

from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.pipeline import Pipeline
from app.models.quality_metric import QualityMetric
from app.models.vulnerability import Vulnerability
from app.repositories.repository_repository import RepositoryRepository
from app.repositories.vulnerability_repository import VulnerabilityRepository
from app.schemas.analytics import AnalyticsResponse, DashboardSummary, TrendPoint


class AnalyticsService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repos = RepositoryRepository(session)
        self.vulns = VulnerabilityRepository(session)

    async def get_dashboard(self) -> AnalyticsResponse:
        total_repos = await self.repos.count_all()
        running = await self._count_pipelines("running")
        success_rate = await self._pipeline_success_rate()
        open_vulns = await self._count_vulnerabilities()
        critical = await self._count_vulnerabilities("critical")
        avg_quality = await self._avg_quality_score()
        avg_coverage = await self._avg_coverage()

        summary = DashboardSummary(
            total_repositories=total_repos,
            active_pipelines=running,
            pipeline_success_rate=success_rate,
            open_vulnerabilities=open_vulns,
            critical_vulnerabilities=critical,
            average_quality_score=avg_quality,
            average_coverage=avg_coverage,
        )

        return AnalyticsResponse(
            summary=summary,
            vulnerability_trend=await self._vuln_trend(),
            coverage_trend=await self._metric_trend("coverage"),
            pipeline_success_trend=await self._pipeline_trend(),
            quality_score_trend=await self._metric_trend("quality_score"),
            severity_breakdown=await self._severity_breakdown(),
            technical_debt_trend=await self._metric_trend("technical_debt_minutes"),
        )

    async def _severity_breakdown(self) -> dict[str, int]:
        counts = await self.vulns.count_by_severity()
        return {
            "critical": counts.get("critical", 0),
            "high": counts.get("high", 0),
            "medium": counts.get("medium", 0),
            "low": counts.get("low", 0),
            "info": counts.get("info", 0),
        }

    async def _count_pipelines(self, status: str) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(Pipeline).where(Pipeline.status == status)
        )
        return result.scalar() or 0

    async def _pipeline_success_rate(self) -> float:
        total = await self.session.execute(select(func.count()).select_from(Pipeline))
        total_count = total.scalar() or 0
        if total_count == 0:
            return 100.0
        success = await self.session.execute(
            select(func.count()).select_from(Pipeline).where(Pipeline.status == "success")
        )
        return round((success.scalar() or 0) / total_count * 100, 2)

    async def _count_vulnerabilities(self, severity: str | None = None) -> int:
        query = select(func.count()).select_from(Vulnerability).where(
            Vulnerability.is_suppressed.is_(False)
        )
        if severity:
            query = query.where(Vulnerability.severity == severity)
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def _avg_quality_score(self) -> float:
        result = await self.session.execute(select(func.avg(QualityMetric.quality_score)))
        return round(float(result.scalar() or 0), 2)

    async def _avg_coverage(self) -> float:
        result = await self.session.execute(select(func.avg(QualityMetric.coverage)))
        return round(float(result.scalar() or 0), 2)

    async def _vuln_trend(self, days: int = 14) -> list[TrendPoint]:
        points = []
        for i in range(days, -1, -1):
            day = datetime.utcnow().date() - timedelta(days=i)
            result = await self.session.execute(
                select(func.count()).select_from(Vulnerability).where(
                    func.date(Vulnerability.created_at) == day
                )
            )
            points.append(TrendPoint(date=day.isoformat(), value=float(result.scalar() or 0)))
        return points

    async def _metric_trend(self, field: str, days: int = 14) -> list[TrendPoint]:
        col = getattr(QualityMetric, field)
        points = []
        for i in range(days, -1, -1):
            day = datetime.utcnow().date() - timedelta(days=i)
            result = await self.session.execute(
                select(func.avg(col)).where(func.date(QualityMetric.created_at) == day)
            )
            points.append(TrendPoint(date=day.isoformat(), value=float(result.scalar() or 0)))
        return points

    async def _pipeline_trend(self, days: int = 14) -> list[TrendPoint]:
        points = []
        for i in range(days, -1, -1):
            day = datetime.utcnow().date() - timedelta(days=i)
            total = await self.session.execute(
                select(func.count()).select_from(Pipeline).where(
                    func.date(Pipeline.created_at) == day
                )
            )
            success = await self.session.execute(
                select(func.count())
                .select_from(Pipeline)
                .where(func.date(Pipeline.created_at) == day, Pipeline.status == "success")
            )
            t = total.scalar() or 0
            rate = (success.scalar() or 0) / t * 100 if t else 100.0
            points.append(TrendPoint(date=day.isoformat(), value=round(rate, 2)))
        return points
