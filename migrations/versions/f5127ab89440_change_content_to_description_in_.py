"""Change content to description in WorkLog model

Revision ID: f5127ab89440
Revises: acfff66b973b
Create Date: 2025-04-16 05:50:38.703182

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f5127ab89440'
down_revision = 'acfff66b973b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('work_logs', sa.Column('description', sa.Text(), nullable=True))
    op.drop_column('work_logs', 'content')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('work_logs', sa.Column('content', sa.TEXT(), autoincrement=False, nullable=True))
    op.drop_column('work_logs', 'description')
    # ### end Alembic commands ###
