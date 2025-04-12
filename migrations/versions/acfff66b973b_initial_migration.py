"""initial migration

Revision ID: acfff66b973b
Revises: 
Create Date: 2025-04-12 18:33:43.054917

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'acfff66b973b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('password_hash', sa.String(length=512), nullable=True),
    sa.Column('is_admin', sa.Boolean(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('user_type', sa.String(length=20), nullable=False),
    sa.Column('account_number', sa.String(length=64), nullable=True),
    sa.Column('phone_number', sa.String(length=20), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_users_email'), ['email'], unique=True)
        batch_op.create_index(batch_op.f('ix_users_username'), ['username'], unique=True)

    op.create_table('links',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('link_code', sa.String(length=64), nullable=True),
    sa.Column('password', sa.String(length=128), nullable=True),
    sa.Column('link_type', sa.String(length=20), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('applicant_name', sa.String(length=100), nullable=True),
    sa.Column('applicant_phone', sa.String(length=20), nullable=True),
    sa.Column('worker_name', sa.String(length=100), nullable=True),
    sa.Column('worker_phone', sa.String(length=20), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('admin_id', sa.Integer(), nullable=True),
    sa.Column('applicant_id', sa.Integer(), nullable=True),
    sa.Column('worker_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['admin_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['applicant_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['worker_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('links', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_links_link_code'), ['link_code'], unique=True)

    op.create_table('work_logs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('work_date', sa.Date(), nullable=False),
    sa.Column('start_time', sa.Time(), nullable=True),
    sa.Column('end_time', sa.Time(), nullable=True),
    sa.Column('content', sa.Text(), nullable=True),
    sa.Column('action', sa.String(length=64), nullable=True),
    sa.Column('details', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('link_id', sa.Integer(), nullable=True),
    sa.Column('worker_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['link_id'], ['links.id'], ),
    sa.ForeignKeyConstraint(['worker_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('work_logs')
    with op.batch_alter_table('links', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_links_link_code'))

    op.drop_table('links')
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_username'))
        batch_op.drop_index(batch_op.f('ix_users_email'))

    op.drop_table('users')
    # ### end Alembic commands ###
