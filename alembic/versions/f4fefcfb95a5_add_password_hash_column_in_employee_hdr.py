"""add password hash column in employee hdr

Revision ID: f4fefcfb95a5
Revises: db9aea29e05d
Create Date: 2025-03-14 20:13:53.712251

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f4fefcfb95a5'
down_revision: Union[str, None] = 'db9aea29e05d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
