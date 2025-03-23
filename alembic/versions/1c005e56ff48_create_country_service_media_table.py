"""create_country_service_media_table

Revision ID: 1c005e56ff48
Revises: 33f63853ceb6
Create Date: 2025-03-24 01:02:46.395883

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text  # Import the text function



# revision identifiers, used by Alembic.
revision: str = '1c005e56ff48'
down_revision: Union[str, None] = '33f63853ceb6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    # Check if the enum type already exists
    gender_enum = sa.Enum('IMAGE', 'VIDEO', name='file_type_enum')

    # Create the `country_service_media` table
    op.create_table(
        'country_service_media',
        sa.Column('image_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('country_id', sa.Integer, sa.ForeignKey('country_hdr.country_id'), nullable=True),
        sa.Column('visa_process_id', sa.Integer, sa.ForeignKey('visa_process_hdr.visa_process_id'), nullable=True),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('file_path', sa.String(255), nullable=False),
        sa.Column('file_type', gender_enum, nullable=False),
        sa.Column('uploaded_at', sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column('is_flag', sa.Boolean, default=False, nullable=False),
        sa.Column('is_icon', sa.Boolean, default=False, nullable=False),
        sa.Column('is_default', sa.Boolean, default=False, nullable=False),
    )

def downgrade():
    # Drop the `country_service_media` table
    op.drop_table('country_service_media')

    # Drop enum types
    op.execute("DROP TYPE IF EXISTS file_type_enum")
