"""Create employee_country_access table

Revision ID: 9d379ee0525d
Revises: 847a4304515e
Create Date: 2025-03-16 16:17:26.017887

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9d379ee0525d'
down_revision: Union[str, None] = '847a4304515e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'employee_country_access',
        sa.Column('country_access_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('employee_id', sa.Integer, sa.ForeignKey('employee_hdr.employee_id'), nullable=False),
        sa.Column('country_id', sa.Integer, sa.ForeignKey('country_hdr.country_id'), nullable=False),
        sa.Column('granted_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('granted_by', sa.Integer, sa.ForeignKey('employee_hdr.employee_id'), nullable=False)
    )


def downgrade() -> None:
    op.drop_table('employee_country_access')