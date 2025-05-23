"""services created_at index
Revision ID: e3f56b464aee
Revises: 00ada6bdd27a
Create Date: 2024-09-12 13:11:06.052441
"""

from alembic import op

# revision identifiers, used by Alembic
revision = "e3f56b464aee"
down_revision = "00ada6bdd27a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index("created_at_idx", "sessions", ["created_at"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index("created_at_idx", table_name="sessions")
    # ### end Alembic commands ###
