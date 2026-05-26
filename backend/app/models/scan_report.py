"""Scan report model."""

from typing import TYPE_CHECKING, Optional
import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.pipeline import Pipeline


class ScanReport(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "scan_reports"

    pipeline_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pipelines.id", ondelete="CASCADE"), index=True
    )
    tool: Mapped[str] = mapped_column(String(50), index=True)
    status: Mapped[str] = mapped_column(String(50), default="completed")
    summary: Mapped[Optional[str]] = mapped_column(Text)
    raw_report: Mapped[Optional[dict]] = mapped_column(JSONB)
    issues_count: Mapped[int] = mapped_column(default=0)

    pipeline: Mapped["Pipeline"] = relationship(back_populates="scan_reports")
