"""Initial Schema

Revision ID: 1
Revises: 
Create Date: 2024-07-10 13:15:35.829445

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('organisation',
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('invite_code', sa.String(), nullable=False),
    sa.Column('logo_url', sa.String(), nullable=True),
    sa.Column('id', sa.String(length=19), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=True),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('description')
    )
    op.create_index(op.f('ix_organisation_created_at'), 'organisation', ['created_at'], unique=False)
    op.create_index(op.f('ix_organisation_invite_code'), 'organisation', ['invite_code'], unique=True)
    op.create_index(op.f('ix_organisation_name'), 'organisation', ['name'], unique=False)
    op.create_index(op.f('ix_organisation_updated_at'), 'organisation', ['updated_at'], unique=False)
    op.create_table('user',
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('username', sa.String(), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('organisation_id', sa.String(length=19), nullable=False),
    sa.Column('id', sa.String(length=19), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=True),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['organisation_id'], ['organisation.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_created_at'), 'user', ['created_at'], unique=False)
    op.create_index(op.f('ix_user_name'), 'user', ['name'], unique=False)
    op.create_index(op.f('ix_user_updated_at'), 'user', ['updated_at'], unique=False)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('cluster',
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('cpu_allocated', sa.Numeric(), nullable=False),
    sa.Column('memory_allocated', sa.Numeric(), nullable=False),
    sa.Column('organisation_id', sa.String(length=19), nullable=False),
    sa.Column('created_by', sa.String(length=19), nullable=False),
    sa.Column('notes', sa.String(), nullable=True),
    sa.Column('id', sa.String(length=19), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=True),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
    sa.ForeignKeyConstraint(['organisation_id'], ['organisation.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cluster_created_at'), 'cluster', ['created_at'], unique=False)
    op.create_index(op.f('ix_cluster_name'), 'cluster', ['name'], unique=False)
    op.create_index(op.f('ix_cluster_updated_at'), 'cluster', ['updated_at'], unique=False)
    op.create_table('deployment',
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('priority', sa.Integer(), nullable=False),
    sa.Column('cpu_allocated', sa.Numeric(), nullable=False),
    sa.Column('memory_allocated', sa.Numeric(), nullable=False),
    sa.Column('path_to_docker_image', sa.String(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('organisation_id', sa.String(length=19), nullable=False),
    sa.Column('cluster_id', sa.String(length=19), nullable=False),
    sa.Column('created_by', sa.String(length=19), nullable=False),
    sa.Column('notes', sa.String(), nullable=True),
    sa.Column('id', sa.String(length=19), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=True),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['cluster_id'], ['cluster.id'], ),
    sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
    sa.ForeignKeyConstraint(['organisation_id'], ['organisation.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_deployment_created_at'), 'deployment', ['created_at'], unique=False)
    op.create_index(op.f('ix_deployment_name'), 'deployment', ['name'], unique=False)
    op.create_index(op.f('ix_deployment_path_to_docker_image'), 'deployment', ['path_to_docker_image'], unique=False)
    op.create_index(op.f('ix_deployment_priority'), 'deployment', ['priority'], unique=False)
    op.create_index(op.f('ix_deployment_status'), 'deployment', ['status'], unique=False)
    op.create_index(op.f('ix_deployment_updated_at'), 'deployment', ['updated_at'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_deployment_updated_at'), table_name='deployment')
    op.drop_index(op.f('ix_deployment_status'), table_name='deployment')
    op.drop_index(op.f('ix_deployment_priority'), table_name='deployment')
    op.drop_index(op.f('ix_deployment_path_to_docker_image'), table_name='deployment')
    op.drop_index(op.f('ix_deployment_name'), table_name='deployment')
    op.drop_index(op.f('ix_deployment_created_at'), table_name='deployment')
    op.drop_table('deployment')
    op.drop_index(op.f('ix_cluster_updated_at'), table_name='cluster')
    op.drop_index(op.f('ix_cluster_name'), table_name='cluster')
    op.drop_index(op.f('ix_cluster_created_at'), table_name='cluster')
    op.drop_table('cluster')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_updated_at'), table_name='user')
    op.drop_index(op.f('ix_user_name'), table_name='user')
    op.drop_index(op.f('ix_user_created_at'), table_name='user')
    op.drop_table('user')
    op.drop_index(op.f('ix_organisation_updated_at'), table_name='organisation')
    op.drop_index(op.f('ix_organisation_name'), table_name='organisation')
    op.drop_index(op.f('ix_organisation_invite_code'), table_name='organisation')
    op.drop_index(op.f('ix_organisation_created_at'), table_name='organisation')
    op.drop_table('organisation')
    # ### end Alembic commands ###