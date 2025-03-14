"""Add last_login and login_count columns to employee_hdr

Revision ID: 6552e2e5f2c2
Revises: 90c8f7eccd73
Create Date: 2025-03-14 22:45:21.696502

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6552e2e5f2c2'
down_revision: Union[str, None] = '90c8f7eccd73'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    # Add last_login and login_count columns
    op.add_column('employee_hdr', sa.Column('last_login', sa.DateTime(), nullable=True))
    op.add_column('employee_hdr', sa.Column('login_count', sa.Integer(), nullable=True, server_default=sa.text('0')))

def downgrade():
    # Remove last_login and login_count columns
    op.drop_column('employee_hdr', 'last_login')
    op.drop_column('employee_hdr', 'login_count')

