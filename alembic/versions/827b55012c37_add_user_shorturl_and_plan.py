"""add User, ShortURL and Plan

Revision ID: 827b55012c37
Revises: 
Create Date: 2025-04-25 10:05:05.484576

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '827b55012c37'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('max_shorturls', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_plans_id'), 'plans', ['id'], unique=False)
    
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('status', sa.Enum(
            'ACTIVE', 'EMAIL_UNVERIFIED', 'BANNED', 'SUSPENDED', 'LOCKED', 
            name='userstatus'
        ), nullable=False),
        sa.Column('shorturls_count', sa.Integer(), nullable=False),
        sa.Column('is_superuser', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('plan_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['plan_id'], ['plans.id'], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    
    op.create_table('shorturls',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('slug', sa.String(length=30), nullable=False),
        sa.Column('original_url', sa.String(), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum(
            'ACTIVE', 'DEACTIVATED', 'BANNED', 'SUSPENDED', 'EXPIRED', 
            name='shorturlstatus'
        ), nullable=False),
        sa.Column('visit_count', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_accessed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_shorturls_id'), 'shorturls', ['id'], unique=False)
    op.create_index(op.f('ix_shorturls_slug'), 'shorturls', ['slug'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_shorturls_slug'), table_name='shorturls')
    op.drop_index(op.f('ix_shorturls_id'), table_name='shorturls')
    op.drop_table('shorturls')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_plans_id'), table_name='plans')
    op.drop_table('plans')
