"""add missing user columns

Revision ID: 75d1541dc08a
Revises: a1f12f2d6b40
Create Date: 2026-02-28 14:32:09.399595

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '75d1541dc08a'
down_revision: Union[str, None] = 'a1f12f2d6b40'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add missing columns to users table
    op.add_column('users', sa.Column('is_email_verified', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('email_verification_token', sa.String(length=64), nullable=True))
    op.add_column('users', sa.Column('email_verification_token_expires', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('brand_color', sa.String(length=7), nullable=True))
    op.add_column('users', sa.Column('logo_url', sa.String(length=500), nullable=True))
    op.add_column('users', sa.Column('keysafe_location', sa.String(length=500), nullable=True))
    op.add_column('users', sa.Column('keysafe_code', sa.String(length=50), nullable=True))
    op.add_column('users', sa.Column('keysafe_instructions', sa.Text(), nullable=True))
    op.create_index(op.f('ix_users_email_verification_token'), 'users', ['email_verification_token'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_users_email_verification_token'), table_name='users')
    op.drop_column('users', 'keysafe_instructions')
    op.drop_column('users', 'keysafe_code')
    op.drop_column('users', 'keysafe_location')
    op.drop_column('users', 'logo_url')
    op.drop_column('users', 'brand_color')
    op.drop_column('users', 'email_verification_token_expires')
    op.drop_column('users', 'email_verification_token')
    op.drop_column('users', 'is_email_verified')
