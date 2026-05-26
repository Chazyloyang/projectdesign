"""Analytics schemas."""

from typing import List, Optional

from pydantic import BaseModel


class TrendPoint(BaseModel):
    date: str
    value: float


class DashboardSummary(BaseModel):
    total_repositories: int
    active_pipelines: int
    pipeline_success_rate: float
    open_vulnerabilities: int
    critical_vulnerabilities: int
    average_quality_score: float
    average_coverage: float


class AnalyticsResponse(BaseModel):
    summary: DashboardSummary
    vulnerability_trend: List[TrendPoint]
    coverage_trend: List[TrendPoint]
    pipeline_success_trend: List[TrendPoint]
    quality_score_trend: List[TrendPoint]
    severity_breakdown: dict[str, int]
    technical_debt_trend: List[TrendPoint]
