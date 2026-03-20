"""add user subscription fields

Revision ID: 001_user_subscription
Revises: 75d1541dc08a
Create Date: 2026-03-20

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_user_subscription'
down_revision = '75d1541dc08a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add user management columns
    op.add_column('users', sa.Column('phone', sa.String(length=50), nullable=True))
    op.add_column('users', sa.Column('company_name', sa.String(length=200), nullable=True))
    op.add_column('users', sa.Column('plan', sa.String(length=20), nullable=True, server_default='free'))
    op.add_column('users', sa.Column('trial_ends_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('max_properties', sa.Integer(), nullable=True, server_default='1'))
    op.add_column('users', sa.Column('stripe_customer_id', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'))
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=True, server_default='false'))
    
    # Add invoice fields
    op.add_column('users', sa.Column('invoice_name', sa.String(length=200), nullable=True))
    op.add_column('users', sa.Column('invoice_address', sa.String(length=500), nullable=True))
    op.add_column('users', sa.Column('invoice_zip', sa.String(length=20), nullable=True))
    op.add_column('users', sa.Column('invoice_city', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('invoice_country', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('invoice_vat_id', sa.String(length=50), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'invoice_vat_id')
    op.drop_column('users', 'invoice_country')
    op.drop_column('users', 'invoice_city')
    op.drop_column('users', 'invoice_zip')
    op.drop_column('users', 'invoice_address')
    op.drop_column('users', 'invoice_name')
    op.drop_column('users', 'is_admin')
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'stripe_customer_id')
    op.drop_column('users', 'max_properties')
    op.drop_column('users', 'trial_ends_at')
    op.drop_column('users', 'plan')
    op.drop_column('users', 'company_name')
    op.drop_column('users', 'phone')