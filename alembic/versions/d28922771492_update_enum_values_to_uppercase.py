"""update_enum_values_to_uppercase

Revision ID: d28922771492
Revises: 341d26666334
Create Date: 2025-03-16 18:26:38.435729

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd28922771492'
down_revision: Union[str, None] = '341d26666334'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Drop existing enum types with CASCADE
    op.execute("DROP TYPE IF EXISTS employee_gender_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS employee_marital_status_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS employee_id_proof_type_enum CASCADE")

    # Create new enum types with uppercase values
    gender_enum = sa.Enum('MALE', 'FEMALE', 'OTHER', name='employee_gender_enum')
    marital_status_enum = sa.Enum('SINGLE', 'MARRIED', 'DIVORCED', 'WIDOWED', name='employee_marital_status_enum')
    id_proof_type_enum = sa.Enum('AADHAR', 'PAN', 'VOTER_ID', 'DRIVING_LICENSE', 'PASSPORT', 'OTHER', name='employee_id_proof_type_enum')

    gender_enum.create(op.get_bind(), checkfirst=True)
    marital_status_enum.create(op.get_bind(), checkfirst=True)
    id_proof_type_enum.create(op.get_bind(), checkfirst=True)

    # Re-add the columns with the new enum types
    op.add_column('employee_hdr', sa.Column('gender', gender_enum))
    op.add_column('employee_hdr', sa.Column('marital_status', marital_status_enum))
    op.add_column('employee_hdr', sa.Column('id_proof_type', id_proof_type_enum))

def downgrade():
    # Drop the new enum types with CASCADE
    op.execute("DROP TYPE IF EXISTS employee_gender_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS employee_marital_status_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS employee_id_proof_type_enum CASCADE")

    # Recreate the old enum types (if needed)
    # Example:
    # old_gender_enum = sa.Enum('Male', 'Female', 'Other', name='employee_gender_enum')
    # old_gender_enum.create(op.get_bind(), checkfirst=True)
    # op.add_column('employee_hdr', sa.Column('gender', old_gender_enum))