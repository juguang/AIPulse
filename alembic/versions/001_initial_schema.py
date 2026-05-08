"""Create initial database schema with all 4 tables.

Revision ID: 001
Revises: None
Create Date: 2026-05-08

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---- source_configs (no FK dependencies) ----
    op.create_table(
        "source_configs",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("crawl_interval", sa.Integer(), nullable=False, server_default=sa.text("30")),
        sa.Column("last_crawled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("consecutive_failures", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("health_score", sa.Float(), nullable=True, server_default=sa.text("1.0")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_source_configs_type"), "source_configs", ["type"])

    # ---- raw_items (FK: source_configs.id) ----
    op.create_table(
        "raw_items",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("source_id", sa.BigInteger(), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("guid", sa.Text(), nullable=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("content_raw", sa.Text(), nullable=True),
        sa.Column("content_normalized", sa.Text(), nullable=True),
        sa.Column("author", sa.String(255), nullable=True),
        sa.Column(
            "published_at", sa.DateTime(timezone=True), nullable=False
        ),
        sa.Column(
            "fetched_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default=sa.text("'pending'"),
        ),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "retry_count", sa.Integer(), nullable=False, server_default=sa.text("0")
        ),
        sa.Column(
            "raw_data",
            postgresql.JSONB(),
            nullable=True,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "metadata",
            postgresql.JSONB(),
            nullable=True,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["source_configs.id"],
            name="fk_raw_items_source_id",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_raw_items_content_hash"), "raw_items", ["content_hash"], unique=True
    )
    op.create_index(
        "uq_raw_items_source_guid",
        "raw_items",
        ["source_id", "guid"],
        unique=True,
        postgresql_nulls_not_distinct=True,
    )
    op.create_index(op.f("ix_raw_items_published_at"), "raw_items", ["published_at"])
    op.create_index(op.f("ix_raw_items_source_id"), "raw_items", ["source_id"])
    op.create_index(op.f("ix_raw_items_status"), "raw_items", ["status"])

    # ---- processed_items (FK: raw_items.id) ----
    op.create_table(
        "processed_items",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("raw_item_id", sa.BigInteger(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column(
            "tags", postgresql.JSONB(), nullable=True, server_default=sa.text("'[]'::jsonb")
        ),
        sa.Column("category", sa.String(50), nullable=True),
        sa.Column(
            "recommended_score", sa.Float(), nullable=True, server_default=sa.text("0.0")
        ),
        sa.Column("recommendation_reason", sa.Text(), nullable=True),
        sa.Column("llm_model_used", sa.String(100), nullable=True),
        sa.Column(
            "input_tokens", sa.Integer(), nullable=True, server_default=sa.text("0")
        ),
        sa.Column(
            "output_tokens", sa.Integer(), nullable=True, server_default=sa.text("0")
        ),
        sa.Column("cost_usd", sa.Float(), nullable=True, server_default=sa.text("0.0")),
        sa.Column(
            "processed_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["raw_item_id"],
            ["raw_items.id"],
            name="fk_processed_items_raw_item_id",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_processed_items_raw_item_id"),
        "processed_items",
        ["raw_item_id"],
        unique=True,
    )
    op.create_index(op.f("ix_processed_items_category"), "processed_items", ["category"])

    # ---- image_cache (no FK dependencies) ----
    op.create_table(
        "image_cache",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("original_url", sa.Text(), nullable=False),
        sa.Column("proxy_path", sa.String(512), nullable=False),
        sa.Column(
            "cached_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("file_size", sa.Integer(), nullable=True),
        sa.Column("content_type", sa.String(100), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_image_cache_original_url"),
        "image_cache",
        ["original_url"],
        unique=True,
    )


def downgrade() -> None:
    # Drop tables in reverse dependency order
    op.drop_table("image_cache")
    op.drop_table("processed_items")
    op.drop_table("raw_items")
    op.drop_table("source_configs")
