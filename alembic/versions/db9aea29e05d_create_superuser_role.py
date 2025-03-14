"""Create superuser role

Revision ID: db9aea29e05d
Revises: 3ce10ddb60fa
Create Date: 2025-03-14 19:50:56.141485

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'db9aea29e05d'
down_revision: Union[str, None] = '3ce10ddb60fa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Insert the superuser role
    op.execute(
        sa.text(
            "INSERT INTO role_hdr (role_name, is_system_role) VALUES ('superuser', true)"
        )
    )


def downgrade() -> None:
    # Delete the superuser role
    op.execute(
        sa.text(
            "DELETE FROM role_hdr WHERE role_name = 'superuser'"
        )
    )
