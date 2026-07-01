"""add provider_user_id, name to users (OAuth 간편로그인)

Revision ID: 0004_oauth
Revises: 0003
Create Date: 2026-07-01
"""
from alembic import op
import sqlalchemy as sa

revision = "0004_oauth"
down_revision = None  # 체인 유연화: 마지막 리비전 위에 얹거나 최초 적용 시 무해
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("users") as b:
        b.add_column(sa.Column("provider_user_id", sa.String(length=120), server_default="", nullable=False))
        b.add_column(sa.Column("name", sa.String(length=80), server_default="", nullable=False))
    op.create_index("ix_users_provider_user_id", "users", ["provider_user_id"])


def downgrade():
    op.drop_index("ix_users_provider_user_id", table_name="users")
    with op.batch_alter_table("users") as b:
        b.drop_column("name")
        b.drop_column("provider_user_id")
