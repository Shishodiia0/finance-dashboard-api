"""add created_at to financial_records

Revision ID: 0002
Revises: 0001
Create Date: 2024-01-02 00:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "financial_records",
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        schema="finance",
    )


def downgrade():
    op.drop_column("financial_records", "created_at", schema="finance")
