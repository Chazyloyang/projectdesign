"""Quality metrics model."""

from typing import TYPE_CHECKING, Optional
import uuid

from sqlalchemy import Float, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.repository import Repository


class QualityMetric(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "quality_metrics"

    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), index=True
    )
    pipeline_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pipelines.id", ondelete="SET NULL"), nullable=True
    )
    coverage: Mapped[Optional[float]] = mapped_column(Float)
    complexity: Mapped[Optional[float]] = mapped_column(Float)
    duplication_percent: Mapped[Optional[float]] = mapped_column(Float)
    technical_debt_minutes: Mapped[Optional[float]] = mapped_column(Float)
    quality_score: Mapped[Optional[float]] = mapped_column(Float, index=True)
    code_smells: Mapped[Optional[int]] = mapped_column(Integer)
    bugs: Mapped[Optional[int]] = mapped_column(Integer)
    vulnerabilities_count: Mapped[Optional[int]] = mapped_column(Integer)

    repository: Mapped["Repository"] = relationship(back_populates="quality_metrics")
