"""Application configuration via environment variables."""

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "DevSecOps Quality Platform"
    environment: str = "development"
    log_level: str = "INFO"
    api_prefix: str = "/api"

    database_url: str = Field(
        default="postgresql+asyncpg://platform:platform_secret@localhost:5432/devsecops_platform"
    )
    database_url_sync: str = Field(
        default="postgresql://platform:platform_secret@localhost:5432/devsecops_platform"
    )
    redis_url: str = "redis://localhost:6379/0"

    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    github_client_id: str = ""
    github_client_secret: str = ""
    github_redirect_uri: str = "http://localhost:8000/api/auth/oauth/github/callback"
    gitlab_client_id: str = ""
    gitlab_client_secret: str = ""
    gitlab_redirect_uri: str = "http://localhost:8000/api/auth/oauth/gitlab/callback"

    sonarqube_url: str = "http://localhost:9000"
    sonarqube_token: str = ""

    cors_origins: str = "http://localhost:3000"
    rate_limit_per_minute: int = 60
    encryption_key: str = "32-byte-base64-key-change-in-prod=="

    seed_admin_email: str = "admin@platform.local"
    seed_admin_password: str = "ChangeMe123!"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors(cls, v: str | List[str]) -> str:
        if isinstance(v, list):
            return ",".join(v)
        return v

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
