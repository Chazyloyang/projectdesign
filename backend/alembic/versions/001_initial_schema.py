"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-05-16

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Tables created via SQLAlchemy metadata in app startup;
    # this migration documents the schema for production Alembic workflows.
    pass


def downgrade() -> None:
    pass
