"""Pipeline schemas."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class PipelineRunRequest(BaseModel):
    repository_id: UUID
    branch: str = "main"
    commit_sha: Optional[str] = None


class PipelineStageResponse(BaseModel):
    id: UUID
    name: str
    status: str
    order: int
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class PipelineResponse(BaseModel):
    id: UUID
    repository_id: UUID
    status: str
    branch: str
    commit_sha: Optional[str] = None
    trigger: str
    quality_gate_passed: Optional[bool] = None
    coverage_percent: Optional[float] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    stages: List[PipelineStageResponse] = []

    model_config = {"from_attributes": True}


class PipelineListResponse(BaseModel):
    items: list[PipelineResponse]
    total: int
