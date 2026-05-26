"""Report generation (PDF and CSV)."""

import csv
import io
from datetime import datetime, timezone
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.pipeline import Pipeline
from app.models.quality_metric import QualityMetric
from app.models.vulnerability import Vulnerability
from app.services.analytics_service import AnalyticsService


class ReportService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.analytics = AnalyticsService(session)

    async def build_security_csv(self) -> bytes:
        vulns = await self._all_vulnerabilities()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            ["severity", "title", "tool", "file_path", "line_number", "repository_id", "created_at"]
        )
        for v in vulns:
            writer.writerow(
                [
                    v.severity,
                    v.title,
                    v.tool,
                    v.file_path or "",
                    v.line_number or "",
                    str(v.repository_id),
                    v.created_at.isoformat() if v.created_at else "",
                ]
            )
        return output.getvalue().encode("utf-8-sig")

    async def build_quality_csv(self) -> bytes:
        metrics = await self._all_quality_metrics()
        pipelines = await self._all_pipelines()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["section", "field", "value"])
        dashboard = await self.analytics.get_dashboard()
        s = dashboard.summary
        for field, val in [
            ("total_repositories", s.total_repositories),
            ("open_vulnerabilities", s.open_vulnerabilities),
            ("pipeline_success_rate", s.pipeline_success_rate),
            ("average_quality_score", s.average_quality_score),
            ("average_coverage", s.average_coverage),
        ]:
            writer.writerow(["summary", field, val])
        writer.writerow([])
        writer.writerow(["pipeline", "id", "repository_id", "status", "branch", "coverage", "quality_gate"])
        for p in pipelines:
            writer.writerow(
                [
                    "pipeline",
                    str(p.id),
                    str(p.repository_id),
                    p.status,
                    p.branch,
                    p.coverage_percent or "",
                    p.quality_gate_passed if p.quality_gate_passed is not None else "",
                ]
            )
        writer.writerow([])
        writer.writerow(["metrics", "repository_id", "quality_score", "coverage", "technical_debt_minutes"])
        for m in metrics:
            writer.writerow(
                [
                    "metric",
                    str(m.repository_id),
                    m.quality_score or "",
                    m.coverage or "",
                    m.technical_debt_minutes or "",
                ]
            )
        return output.getvalue().encode("utf-8-sig")

    async def build_security_pdf(self) -> bytes:
        vulns = await self._all_vulnerabilities()
        dashboard = await self.analytics.get_dashboard()
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story: list[Any] = []

        story.append(Paragraph("DevSecOps Platform — Security Report", styles["Title"]))
        story.append(
            Paragraph(
                f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
                styles["Normal"],
            )
        )
        story.append(Spacer(1, 12))
        s = dashboard.summary
        summary_data = [
            ["Open vulnerabilities", str(s.open_vulnerabilities)],
            ["Critical", str(s.critical_vulnerabilities)],
            ["Pipeline success rate", f"{s.pipeline_success_rate}%"],
            ["Average quality score", f"{s.average_quality_score}%"],
        ]
        t = Table([["Metric", "Value"]] + summary_data, colWidths=[220, 280])
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4f46e5")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ]
            )
        )
        story.append(t)
        story.append(Spacer(1, 16))
        story.append(Paragraph("Findings", styles["Heading2"]))

        if not vulns:
            story.append(Paragraph("No vulnerabilities recorded.", styles["Normal"]))
        else:
            rows = [["Severity", "Title", "Tool", "Location"]]
            for v in vulns[:50]:
                loc = f"{v.file_path or '-'}" + (f":{v.line_number}" if v.line_number else "")
                title = (v.title[:60] + "…") if len(v.title) > 60 else v.title
                rows.append([v.severity, title, v.tool, loc])
            ft = Table(rows, colWidths=[70, 200, 70, 160])
            ft.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.25, colors.grey)]))
            story.append(ft)
            if len(vulns) > 50:
                story.append(Paragraph(f"… and {len(vulns) - 50} more findings (see CSV export).", styles["Normal"]))

        doc.build(story)
        return buffer.getvalue()

    async def build_quality_pdf(self) -> bytes:
        metrics = await self._all_quality_metrics()
        pipelines = await self._all_pipelines()
        dashboard = await self.analytics.get_dashboard()
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story: list[Any] = []

        story.append(Paragraph("DevSecOps Platform — Quality Report", styles["Title"]))
        story.append(
            Paragraph(
                f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
                styles["Normal"],
            )
        )
        story.append(Spacer(1, 12))
        s = dashboard.summary
        story.append(
            Paragraph(
                f"Repositories: {s.total_repositories} | Avg coverage: {s.average_coverage}% | "
                f"Avg quality: {s.average_quality_score}%",
                styles["Normal"],
            )
        )
        story.append(Spacer(1, 12))
        story.append(Paragraph("Recent pipelines", styles["Heading2"]))
        rows = [["Status", "Branch", "Coverage %", "Gate"]]
        for p in pipelines[:20]:
            rows.append(
                [
                    p.status,
                    p.branch,
                    str(p.coverage_percent or "-"),
                    "Pass" if p.quality_gate_passed else "Fail" if p.quality_gate_passed is False else "-",
                ]
            )
        pt = Table(rows, colWidths=[80, 120, 100, 80])
        pt.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.25, colors.grey)]))
        story.append(pt)
        story.append(Spacer(1, 16))
        story.append(Paragraph("Quality metrics", styles["Heading2"]))
        mrows = [["Repository", "Score", "Coverage", "Debt (min)"]]
        for m in metrics[:20]:
            mrows.append(
                [
                    str(m.repository_id)[:8] + "…",
                    str(m.quality_score or "-"),
                    str(m.coverage or "-"),
                    str(m.technical_debt_minutes or "-"),
                ]
            )
        mt = Table(mrows, colWidths=[120, 80, 80, 100])
        mt.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.25, colors.grey)]))
        story.append(mt)

        doc.build(story)
        return buffer.getvalue()

    async def _all_vulnerabilities(self) -> list[Vulnerability]:
        result = await self.session.execute(
            select(Vulnerability)
            .where(Vulnerability.is_suppressed.is_(False))
            .order_by(Vulnerability.created_at.desc())
            .limit(500)
        )
        return list(result.scalars().all())

    async def _all_pipelines(self) -> list[Pipeline]:
        result = await self.session.execute(
            select(Pipeline).order_by(Pipeline.created_at.desc()).limit(200)
        )
        return list(result.scalars().all())

    async def _all_quality_metrics(self) -> list[QualityMetric]:
        result = await self.session.execute(
            select(QualityMetric).order_by(QualityMetric.created_at.desc()).limit(200)
        )
        return list(result.scalars().all())
