"""Repository model."""

from typing import TYPE_CHECKING, List, Optional
import uuid

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.pipeline import Pipeline
    from app.models.vulnerability import Vulnerability
    from app.models.quality_metric import QualityMetric


class Repository(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "repositories"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)  # github, gitlab, bitbucket
    url: Mapped[str] = mapped_column(Text, nullable=False)
    external_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    default_branch: Mapped[str] = mapped_column(String(100), default="main")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    webhook_secret: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    access_token_encrypted: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    organization: Mapped["Organization"] = relationship(back_populates="repositories")
    pipelines: Mapped[List["Pipeline"]] = relationship(
        back_populates="repository", cascade="all, delete-orphan"
    )
    vulnerabilities: Mapped[List["Vulnerability"]] = relationship(
        back_populates="repository", cascade="all, delete-orphan"
    )
    quality_metrics: Mapped[List["QualityMetric"]] = relationship(
        back_populates="repository", cascade="all, delete-orphan"
    )
