"""Add employee details to employee_hdr table

Revision ID: 341d26666334
Revises: 9d379ee0525d
Create Date: 2025-03-16 16:17:58.029418

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '341d26666334'
down_revision: Union[str, None] = '9d379ee0525d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Define the enum types
    gender_enum = sa.Enum('Male', 'Female', 'Other', name='employee_gender_enum')
    marital_status_enum = sa.Enum('Single', 'Married', 'Divorced', 'Widowed', name='employee_marital_status_enum')
    id_proof_type_enum = sa.Enum('Aadhar', 'PAN', 'Voter ID', 'Driving License', 'Passport', 'Other', name='employee_id_proof_type_enum')

    # Create the enum types in the database
    gender_enum.create(op.get_bind(), checkfirst=True)
    marital_status_enum.create(op.get_bind(), checkfirst=True)
    id_proof_type_enum.create(op.get_bind(), checkfirst=True)

    # Add new columns to the table
    op.add_column('employee_hdr', sa.Column('employee_title', sa.String(50)))
    op.add_column('employee_hdr', sa.Column('first_name', sa.String(100)))
    op.add_column('employee_hdr', sa.Column('middle_name', sa.String(100)))
    op.add_column('employee_hdr', sa.Column('last_name', sa.String(100)))
    op.add_column('employee_hdr', sa.Column('gender', gender_enum))
    op.add_column('employee_hdr', sa.Column('dob', sa.DateTime))
    op.add_column('employee_hdr', sa.Column('emergency_contact', sa.String(20)))
    op.add_column('employee_hdr', sa.Column('marital_status', marital_status_enum))
    op.add_column('employee_hdr', sa.Column('id_proof_type', id_proof_type_enum))
    op.add_column('employee_hdr', sa.Column('id_number', sa.String(50)))
    op.add_column('employee_hdr', sa.Column('address', sa.String))
    op.add_column('employee_hdr', sa.Column('pincode', sa.String(10)))

    # Drop the old column
    op.drop_column('employee_hdr', 'employee_name')


def downgrade() -> None:
    # Add back the employee_name column
    op.add_column('employee_hdr', sa.Column('employee_name', sa.String()))

    # Drop the new columns
    op.drop_column('employee_hdr', 'pincode')
    op.drop_column('employee_hdr', 'address')
    op.drop_column('employee_hdr', 'id_number')
    op.drop_column('employee_hdr', 'id_proof_type')
    op.drop_column('employee_hdr', 'marital_status')
    op.drop_column('employee_hdr', 'emergency_contact')
    op.drop_column('employee_hdr', 'dob')
    op.drop_column('employee_hdr', 'gender')
    op.drop_column('employee_hdr', 'last_name')
    op.drop_column('employee_hdr', 'middle_name')
    op.drop_column('employee_hdr', 'first_name')
    op.drop_column('employee_hdr', 'employee_title')

    # Drop enum types
    op.execute("DROP TYPE IF EXISTS employee_gender_enum")
    op.execute("DROP TYPE IF EXISTS employee_marital_status_enum")
    op.execute("DROP TYPE IF EXISTS employee_id_proof_type_enum")