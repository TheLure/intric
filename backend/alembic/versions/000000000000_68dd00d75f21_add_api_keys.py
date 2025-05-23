"""add api keys
Revision ID: 68dd00d75f21
Revises: 9271779d8dc3
Create Date: 2023-12-19 10:21:04.963641
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic
revision = '68dd00d75f21'
down_revision = '9271779d8dc3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'api_keys',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(), nullable=False),
        sa.Column('truncated_key', sa.String(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column(
            'created_at',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.Column(
            'updated_at',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id'),
    )
    op.create_index(op.f('ix_api_keys_key'), 'api_keys', ['key'], unique=False)
    op.drop_index('ix_users_api_key', table_name='users')
    op.drop_column('users', 'api_key')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        'users', sa.Column('api_key', sa.VARCHAR(), autoincrement=False, nullable=True)
    )
    op.create_index('ix_users_api_key', 'users', ['api_key'], unique=False)
    op.drop_index(op.f('ix_api_keys_key'), table_name='api_keys')
    op.drop_table('api_keys')
    # ### end Alembic commands ###
