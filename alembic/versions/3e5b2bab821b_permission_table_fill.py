"""permission table fill

Revision ID: 3e5b2bab821b
Revises: 430190692992
Create Date: 2025-04-10 01:18:04.796652

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.config.database import Base
from app.models.permissions import Permissions

# revision identifiers, used by Alembic.
revision: str = '3e5b2bab821b'
down_revision: Union[str, None] = '430190692992'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    domains = ['roles', 'visa', 'vendors', 'coupons', 'application']
    actions = [
        ('CREATE', 'POST'),
        ('READ', 'GET'),
        ('UPDATE', 'PUT'),
        ('DELETE', 'DELETE')
    ]

    permissions_data = []  # Store data to insert
    for domain in domains:
        for action, method in actions:
            permissions_data.append({
                'permission_name': f'can {action.lower()} on {domain}',
                'description': f'Allows {action.lower()} operation on {domain}',
                'resource': domain,
                'action': action,
                'method': method
            })

    # Use the table name as a string
    # op.bulk_insert('permissions', permissions_data)
        # Use op.execute with table.insert()
    permissions_table = sa.Table('permissions', Base.metadata, autoload_with=op.get_bind())
    op.execute(permissions_table.insert().values(permissions_data))


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DELETE FROM permissions")