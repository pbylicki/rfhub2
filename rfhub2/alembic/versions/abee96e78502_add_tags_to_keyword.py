"""create tags column for keyword table

Revision ID: abee96e78502
Revises: c54a916ec6c8
Create Date: 2020-04-04 12:50:17.064642

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "abee96e78502"
down_revision = "c54a916ec6c8"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("keyword", sa.Column("tags", sa.Text, nullable=True))


def downgrade():
    op.drop_column("keyword", "tags")
