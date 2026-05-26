"""Repository schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class RepositoryCreate(BaseModel):
    organization_id: UUID
    name: str = Field(min_length=1, max_length=255)
    provider: str = Field(pattern="^(github|gitlab|bitbucket)$")
    url: str
    external_id: Optional[str] = None
    default_branch: str = "main"
    access_token: Optional[str] = None


class RepositoryResponse(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    provider: str
    url: str
    default_branch: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class RepositoryListResponse(BaseModel):
    items: list[RepositoryResponse]
    total: int
