"""OAuth2 integration for GitHub and GitLab."""

from urllib.parse import urlencode
from uuid import uuid4

import httpx
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import create_access_token, create_refresh_token, get_password_hash
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenResponse

settings = get_settings()


class OAuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.users = UserRepository(session)

    @staticmethod
    def github_authorize_url() -> str:
        params = {
            "client_id": settings.github_client_id,
            "redirect_uri": settings.github_redirect_uri,
            "scope": "read:user user:email repo",
        }
        return f"https://github.com/login/oauth/authorize?{urlencode(params)}"

    @staticmethod
    def gitlab_authorize_url() -> str:
        params = {
            "client_id": settings.gitlab_client_id,
            "redirect_uri": settings.gitlab_redirect_uri,
            "response_type": "code",
            "scope": "read_user read_api",
        }
        return f"https://gitlab.com/oauth/authorize?{urlencode(params)}"

    async def github_callback(self, code: str) -> TokenResponse:
        if not settings.github_client_id:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="GitHub OAuth not configured")
        async with httpx.AsyncClient() as client:
            token_resp = await client.post(
                "https://github.com/login/oauth/access_token",
                json={
                    "client_id": settings.github_client_id,
                    "client_secret": settings.github_client_secret,
                    "code": code,
                },
                headers={"Accept": "application/json"},
            )
            token_data = token_resp.json()
            access = token_data.get("access_token")
            if not access:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OAuth failed")
            user_resp = await client.get(
                "https://api.github.com/user",
                headers={"Authorization": f"Bearer {access}"},
            )
            profile = user_resp.json()
        return await self._upsert_oauth_user("github", str(profile["id"]), profile.get("email") or f"{profile['login']}@github.local", profile.get("name") or profile["login"], profile.get("avatar_url"))

    async def gitlab_callback(self, code: str) -> TokenResponse:
        if not settings.gitlab_client_id:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="GitLab OAuth not configured")
        async with httpx.AsyncClient() as client:
            token_resp = await client.post(
                "https://gitlab.com/oauth/token",
                data={
                    "client_id": settings.gitlab_client_id,
                    "client_secret": settings.gitlab_client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": settings.gitlab_redirect_uri,
                },
            )
            token_data = token_resp.json()
            access = token_data.get("access_token")
            user_resp = await client.get(
                "https://gitlab.com/api/v4/user",
                headers={"Authorization": f"Bearer {access}"},
            )
            profile = user_resp.json()
        return await self._upsert_oauth_user("gitlab", str(profile["id"]), profile.get("email") or f"{profile['username']}@gitlab.local", profile.get("name") or profile["username"], profile.get("avatar_url"))

    async def _upsert_oauth_user(
        self, provider: str, oauth_id: str, email: str, name: str, avatar: str | None
    ) -> TokenResponse:
        user = await self.users.get_by_email(email)
        if not user:
            user = User(
                name=name,
                email=email,
                password_hash=get_password_hash(str(uuid4())),
                role="developer",
                oauth_provider=provider,
                oauth_id=oauth_id,
                avatar_url=avatar,
            )
            user = await self.users.create(user)
        access = create_access_token(str(user.id), {"role": user.role})
        refresh = create_refresh_token(str(user.id))
        return TokenResponse(access_token=access, refresh_token=refresh)
