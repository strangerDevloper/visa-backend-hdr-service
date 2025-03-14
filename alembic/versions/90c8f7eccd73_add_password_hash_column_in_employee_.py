"""add password hash column in employee hdr a

Revision ID: 90c8f7eccd73
Revises: f4fefcfb95a5
Create Date: 2025-03-14 20:21:40.416755

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '90c8f7eccd73'
down_revision: Union[str, None] = 'f4fefcfb95a5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('employee_hdr', sa.Column('password_hash', sa.String, nullable=False))



def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('employee_hdr', 'password_hash')

