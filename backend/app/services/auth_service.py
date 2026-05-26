"""Authentication service."""

import hashlib
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    verify_token,
)
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenResponse, UserRegister

settings = get_settings()


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.users = UserRepository(session)
        self.audit = AuditRepository(session)

    async def register(self, data: UserRegister) -> User:
        existing = await self.users.get_by_email(data.email)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
        user = User(
            name=data.name,
            email=data.email,
            password_hash=get_password_hash(data.password),
            role="developer",
        )
        return await self.users.create(user)

    async def login(self, email: str, password: str, ip: str | None = None) -> TokenResponse:
        user = await self.users.get_by_email(email)
        if not user or not user.password_hash or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        tokens = await self._issue_tokens(user)
        await self.audit.log("login", "user", str(user.id), user.id, ip)
        return tokens

    async def refresh(self, refresh_token: str) -> TokenResponse:
        user_id = verify_token(refresh_token, "refresh")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        user = await self.users.get_by_id(UUID(user_id))
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return await self._issue_tokens(user)

    async def _issue_tokens(self, user: User) -> TokenResponse:
        access = create_access_token(str(user.id), {"role": user.role, "email": user.email})
        refresh = create_refresh_token(str(user.id))
        token_hash = hashlib.sha256(refresh.encode()).hexdigest()
        rt = RefreshToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days),
        )
        self.session.add(rt)
        await self.session.flush()
        return TokenResponse(access_token=access, refresh_token=refresh)
