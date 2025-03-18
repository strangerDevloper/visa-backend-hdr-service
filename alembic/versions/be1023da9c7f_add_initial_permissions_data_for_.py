"""add initial permissions data for employee user and countries domain

Revision ID: be1023da9c7f
Revises: c9c89d0e8d04
Create Date: 2025-03-18 22:00:44.822923

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Integer, Text

from app.models.permissions import ActionEnum
from app.models.permissions import MethodEnum

# revision identifiers, used by Alembic.
revision: str = 'be1023da9c7f'
down_revision: Union[str, None] = 'c9c89d0e8d04'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade():
    permissions_table = table(
        'permissions',
        column('permission_id', Integer),
        column('permission_name', String),
        column('description', Text),
        column('resource', String),
        column('action', sa.Enum(ActionEnum)),
        column('method', sa.Enum(MethodEnum))
    )

    domains = ['users', 'employees', 'countries']
    actions = [
        ('CREATE', 'POST'),
        ('READ', 'GET'),
        ('UPDATE', 'PUT'),
        ('DELETE', 'DELETE')
    ]

    for domain in domains:
        for action, method in actions:
            op.bulk_insert(permissions_table, [
                {
                    'permission_name': f'can {action.lower()} on {domain}',
                    'description': f'Allows {action.lower()} operation on {domain}',
                    'resource': domain,
                    'action': action,
                    'method': method
                }
            ])

def downgrade():
    op.execute("DELETE FROM permissions")