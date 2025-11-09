"""Add profile fields to users

Revision ID: 7f2c3d1a9add
Revises: 551efcf567fd
Create Date: 2025-10-30

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7f2c3d1a9add'
down_revision = '551efcf567fd'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('profile_photo_url', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('description', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('users', 'description')
    op.drop_column('users', 'profile_photo_url')