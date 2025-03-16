"""update visa type table

Revision ID: c9c89d0e8d04
Revises: 859f34a3bec0
Create Date: 2025-03-16 23:46:42.900310

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c9c89d0e8d04'
down_revision: Union[str, None] = '859f34a3bec0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add the new `country_id` column
    op.add_column('employee_visa_type_access', sa.Column('country_id', sa.Integer, nullable=False))

    # Create a foreign key constraint for `country_id`
    op.create_foreign_key(
        'fk_employee_visa_type_access_country_id',
        'employee_visa_type_access', 'country_hdr',
        ['country_id'], ['country_id']
    )

    # Modify the `visa_process_id` column to be nullable
    op.alter_column('employee_visa_type_access', 'visa_process_id',
                    existing_type=sa.Integer,
                    nullable=True)

def downgrade() -> None:
    # Drop the foreign key constraint for `country_id`
    op.drop_constraint('fk_employee_visa_type_access_country_id', 'employee_visa_type_access', type_='foreignkey')

    # Drop the `country_id` column
    op.drop_column('employee_visa_type_access', 'country_id')

    # Modify the `visa_process_id` column to be non-nullable
    op.alter_column('employee_visa_type_access', 'visa_process_id',
                    existing_type=sa.Integer,
                    nullable=False)