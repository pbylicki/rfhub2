"""Add suite model

Revision ID: d3ab100869e0
Revises: abee96e78502
Create Date: 2020-11-28 22:34:10.042146

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d3ab100869e0"
down_revision = "abee96e78502"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "suite",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("longname", sa.Text(), nullable=False),
        sa.Column("doc", sa.Text(), nullable=True),
        sa.Column("source", sa.Text(), nullable=True),
        sa.Column("keywords", sa.Text(), nullable=False),
        sa.Column("metadata_items", sa.Text(), nullable=False),
        sa.Column("is_root", sa.Boolean(), nullable=False),
        sa.Column("rpa", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_suite_name"), "suite", ["name"], unique=False)
    op.create_index(op.f("ix_suite_longname"), "suite", ["longname"], unique=True)
    op.create_table(
        "suiterel",
        sa.Column("parent_id", sa.Integer(), nullable=False),
        sa.Column("child_id", sa.Integer(), nullable=False),
        sa.Column("degree", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("parent_id", "child_id"),
        sa.ForeignKeyConstraint(["parent_id"], ["suite.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["child_id"], ["suite.id"], ondelete="CASCADE"),
    )
    op.create_table(
        "testcase",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("suite_id", sa.Integer(), nullable=False),
        sa.Column("line", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("doc", sa.Text(), nullable=True),
        sa.Column("source", sa.Text(), nullable=True),
        sa.Column("template", sa.Text(), nullable=True),
        sa.Column("timeout", sa.Text(), nullable=True),
        sa.Column("tags", sa.Text(), nullable=False),
        sa.Column("keywords", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["suite_id"], ["suite.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_testcase_name"), "testcase", ["name"], unique=False)
    op.create_index(
        op.f("ix_testcase_suite_id_name"), "testcase", ["suite_id", "name"], unique=True
    )
    # ### end Alembic commands ###


def downgrade():
    op.drop_index(op.f("ix_testcase_suite_id_name"), table_name="testcase")
    op.drop_index(op.f("ix_testcase_name"), table_name="testcase")
    op.drop_table("testcase")
    op.drop_table("suiterel")
    op.drop_index(op.f("ix_suite_longname"), table_name="suite")
    op.drop_index(op.f("ix_suite_name"), table_name="suite")
    op.drop_table("suite")
    # ### end Alembic commands ###
