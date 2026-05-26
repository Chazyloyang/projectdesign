"""Prometheus metrics for the platform."""

from prometheus_client import Counter, Gauge, Histogram

PIPELINE_RUNS = Counter(
    "platform_pipeline_runs_total",
    "Total pipeline runs",
    ["status", "repository_id"],
)
SCAN_RUNS = Counter(
    "platform_scan_runs_total",
    "Total scan runs",
    ["tool", "status"],
)
VULNERABILITIES_FOUND = Counter(
    "platform_vulnerabilities_total",
    "Vulnerabilities discovered",
    ["severity"],
)
ACTIVE_PIPELINES = Gauge("platform_active_pipelines", "Currently running pipelines")
API_LATENCY = Histogram(
    "platform_api_request_duration_seconds",
    "API request latency",
    ["method", "endpoint"],
)
QUALITY_SCORE = Gauge(
    "platform_quality_score",
    "Latest quality score per repository",
    ["repository_id"],
)
