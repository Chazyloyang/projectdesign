"""Scan result types."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ScanFinding:
    severity: str
    title: str
    tool: str
    description: Optional[str] = None
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    rule_id: Optional[str] = None
    cwe_id: Optional[str] = None


@dataclass
class ScanResult:
    tool: str
    status: str  # success, failed, skipped
    findings: List[ScanFinding] = field(default_factory=list)
    summary: Optional[str] = None
    raw: Optional[Dict[str, Any]] = None
    coverage_percent: Optional[float] = None
    quality_score: Optional[float] = None
