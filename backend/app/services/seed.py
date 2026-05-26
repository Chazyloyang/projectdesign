"""Database seeding for initial admin and demo data."""

import logging
import uuid

from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import get_password_hash
from app.db.session import AsyncSessionLocal
from app.models.organization import Organization, OrganizationMember
from app.models.user import User

logger = logging.getLogger(__name__)
settings = get_settings()

DEFAULT_ORG_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
VALID_ADMIN_EMAIL = "admin@example.com"


async def seed_database() -> None:
    async with AsyncSessionLocal() as session:
        # Migrate legacy admin email
        legacy = await session.execute(select(User).where(User.email == "admin@platform.local"))
        legacy_user = legacy.scalar_one_or_none()
        if legacy_user:
            legacy_user.email = VALID_ADMIN_EMAIL
            await session.commit()
            logger.info("Migrated admin email to %s", VALID_ADMIN_EMAIL)

        existing_admin = await session.execute(
            select(User).where(User.email == VALID_ADMIN_EMAIL)
        )
        if existing_admin.scalar_one_or_none():
            return

        org_result = await session.execute(
            select(Organization).where(Organization.id == DEFAULT_ORG_ID)
        )
        org = org_result.scalar_one_or_none()
        if not org:
            org = Organization(
                id=DEFAULT_ORG_ID,
                name="Default Organization",
                slug="default",
            )
            session.add(org)
            await session.flush()

        admin = User(
            name="Platform Admin",
            email=VALID_ADMIN_EMAIL,
            password_hash=get_password_hash(settings.seed_admin_password),
            role="admin",
        )
        session.add(admin)
        await session.flush()

        member_check = await session.execute(
            select(OrganizationMember).where(
                OrganizationMember.organization_id == DEFAULT_ORG_ID,
                OrganizationMember.user_id == admin.id,
            )
        )
        if not member_check.scalar_one_or_none():
            session.add(
                OrganizationMember(
                    organization_id=DEFAULT_ORG_ID,
                    user_id=admin.id,
                    role="admin",
                )
            )
        await session.commit()
        logger.info("Seeded admin user: %s", VALID_ADMIN_EMAIL)
