"""add lot_id and qty to berita_acara_items

Revision ID: 0b3a1c2d4e5f
Revises: 092a2fafedd7
Create Date: 2026-06-26
"""
from alembic import op
import sqlalchemy as sa

revision = "0b3a1c2d4e5f"
down_revision = "092a2fafedd7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "berita_acara_items",
        sa.Column("lot_id", sa.String(100), nullable=True),
    )
    op.add_column(
        "berita_acara_items",
        sa.Column("qty", sa.DECIMAL(10, 2), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("berita_acara_items", "qty")
    op.drop_column("berita_acara_items", "lot_id")
