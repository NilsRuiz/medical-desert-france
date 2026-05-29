"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-05-28
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "communes",
        sa.Column("code", sa.String(length=8), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("department_code", sa.String(length=4), nullable=True),
        sa.Column("department_name", sa.String(length=255), nullable=True),
        sa.Column("region_code", sa.String(length=4), nullable=True),
        sa.Column("region_name", sa.String(length=255), nullable=True),
        sa.Column("population", sa.Integer(), nullable=True),
        sa.Column("apl_score", sa.Float(), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("code"),
    )
    op.create_index("ix_communes_department_code", "communes", ["department_code"])
    op.create_index("ix_communes_name", "communes", ["name"])
    op.create_index("ix_communes_region_code", "communes", ["region_code"])
    op.create_index("ix_communes_region_name", "communes", ["region_name"])

    op.create_table(
        "commune_predictions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("commune_code", sa.String(length=8), nullable=False),
        sa.Column("model_version", sa.String(length=128), nullable=False),
        sa.Column("risk_class", sa.String(length=32), nullable=False),
        sa.Column("risk_score", sa.Float(), nullable=False),
        sa.Column("predicted_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["commune_code"], ["communes.code"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("commune_code", "model_version", name="uq_prediction_commune_model"),
    )
    op.create_index("ix_commune_predictions_commune_code", "commune_predictions", ["commune_code"])
    op.create_index("ix_commune_predictions_model_version", "commune_predictions", ["model_version"])
    op.create_index("ix_commune_predictions_risk_class", "commune_predictions", ["risk_class"])

    op.create_table(
        "dashboard_metrics",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("scope", sa.String(length=32), nullable=False),
        sa.Column("scope_key", sa.String(length=64), nullable=False),
        sa.Column("label", sa.String(length=255), nullable=False),
        sa.Column("metric_name", sa.String(length=128), nullable=False),
        sa.Column("metric_value", sa.Float(), nullable=False),
        sa.Column("model_version", sa.String(length=128), nullable=False),
        sa.Column("computed_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("scope", "scope_key", "metric_name", "model_version", name="uq_dashboard_metric"),
    )
    op.create_index("ix_dashboard_metrics_metric_name", "dashboard_metrics", ["metric_name"])
    op.create_index("ix_dashboard_metrics_model_version", "dashboard_metrics", ["model_version"])
    op.create_index("ix_dashboard_metrics_scope", "dashboard_metrics", ["scope"])
    op.create_index("ix_dashboard_metrics_scope_key", "dashboard_metrics", ["scope_key"])


def downgrade() -> None:
    op.drop_table("dashboard_metrics")
    op.drop_table("commune_predictions")
    op.drop_table("communes")
