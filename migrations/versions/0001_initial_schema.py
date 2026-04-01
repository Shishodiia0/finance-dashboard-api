"""initial schema

Revision ID: 0001
Revises:
Create Date: 2024-01-01 00:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE SCHEMA IF NOT EXISTS finance")
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("email", sa.String, nullable=False, unique=True),
        sa.Column("full_name", sa.String, nullable=False),
        sa.Column("hashed_password", sa.String, nullable=False),
        sa.Column("role", sa.Enum("viewer", "analyst", "admin", name="role", schema="finance"), nullable=False, server_default="viewer"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        schema="finance",
    )
    op.create_index("ix_finance_users_email", "users", ["email"], schema="finance")

    op.create_table(
        "financial_records",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("amount", sa.Float, nullable=False),
        sa.Column("type", sa.Enum("income", "expense", name="recordtype", schema="finance"), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("date", sa.Date, nullable=False),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("is_deleted", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("owner_id", sa.Integer, sa.ForeignKey("finance.users.id"), nullable=False),
        schema="finance",
    )


def downgrade():
    op.drop_table("financial_records", schema="finance")
    op.drop_table("users", schema="finance")
    op.execute("DROP TYPE IF EXISTS finance.role")
    op.execute("DROP TYPE IF EXISTS finance.recordtype")
