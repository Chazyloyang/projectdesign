"""Pipeline and stage models."""

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
import uuid

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.repository import Repository
    from app.models.scan_report import ScanReport


class Pipeline(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "pipelines"

    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), index=True
    )
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True)
    branch: Mapped[str] = mapped_column(String(100), default="main")
    commit_sha: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    trigger: Mapped[str] = mapped_column(String(50), default="manual")
    quality_gate_passed: Mapped[Optional[bool]] = mapped_column(nullable=True)
    coverage_percent: Mapped[Optional[float]] = mapped_column(nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    repository: Mapped["Repository"] = relationship(back_populates="pipelines")
    stages: Mapped[List["PipelineStage"]] = relationship(
        back_populates="pipeline", cascade="all, delete-orphan", order_by="PipelineStage.order"
    )
    scan_reports: Mapped[List["ScanReport"]] = relationship(back_populates="pipeline")


class PipelineStage(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "pipeline_stages"

    pipeline_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pipelines.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    order: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    log_output: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    pipeline: Mapped["Pipeline"] = relationship(back_populates="stages")
