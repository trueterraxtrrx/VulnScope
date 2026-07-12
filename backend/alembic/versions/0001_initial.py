"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-26
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_organizations_name", "organizations", ["name"], unique=True)

    op.create_table(
        "cves",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("cve_id", sa.String(32), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("severity", sa.String(32), nullable=False),
        sa.Column("cvss_score", sa.Float(), nullable=False),
        sa.Column("published_at", sa.DateTime()),
        sa.Column("references", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_cves_cve_id", "cves", ["cve_id"], unique=True)
    op.create_index("ix_cves_severity", "cves", ["severity"])

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("full_name", sa.String(255)),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_organization_id", "users", ["organization_id"])

    op.create_table(
        "api_keys",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("key_prefix", sa.String(16), nullable=False),
        sa.Column("hashed_key", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("last_used_at", sa.DateTime()),
    )
    op.create_index("ix_api_keys_organization_id", "api_keys", ["organization_id"])
    op.create_index("ix_api_keys_user_id", "api_keys", ["user_id"])
    op.create_index("ix_api_keys_key_prefix", "api_keys", ["key_prefix"])

    op.create_table(
        "assets",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("hostname", sa.String(255), nullable=False),
        sa.Column("ip_address", sa.String(64)),
        sa.Column("os_name", sa.String(128)),
        sa.Column("os_version", sa.String(128)),
        sa.Column("environment", sa.String(64), nullable=False),
        sa.Column("owner", sa.String(255)),
        sa.Column("criticality", sa.Integer(), nullable=False),
        sa.Column("last_seen_at", sa.DateTime()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_assets_organization_id", "assets", ["organization_id"])
    op.create_index("ix_assets_hostname", "assets", ["hostname"])

    op.create_table(
        "software_packages",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("asset_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("assets.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("version", sa.String(128), nullable=False),
        sa.Column("vendor", sa.String(255)),
        sa.Column("package_type", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_software_packages_organization_id", "software_packages", ["organization_id"])
    op.create_index("ix_software_packages_asset_id", "software_packages", ["asset_id"])
    op.create_index("ix_software_packages_name", "software_packages", ["name"])

    op.create_table(
        "asset_vulnerabilities",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("asset_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("assets.id"), nullable=False),
        sa.Column("software_package_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("software_packages.id"), nullable=False),
        sa.Column("cve_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("cves.id"), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("risk_score", sa.Float(), nullable=False),
        sa.Column("detected_at", sa.DateTime(), nullable=False),
        sa.Column("fixed_at", sa.DateTime()),
    )
    for name in ("organization_id", "asset_id", "software_package_id", "cve_id", "status", "risk_score"):
        op.create_index(f"ix_asset_vulnerabilities_{name}", "asset_vulnerabilities", [name])

    op.create_table(
        "remediation_tasks",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("asset_vulnerability_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("asset_vulnerabilities.id")),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("assignee", sa.String(255)),
        sa.Column("due_date", sa.DateTime()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_remediation_tasks_organization_id", "remediation_tasks", ["organization_id"])
    op.create_index("ix_remediation_tasks_status", "remediation_tasks", ["status"])

    op.create_table(
        "imports",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("source", sa.String(128), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("summary", postgresql.JSONB(), nullable=False),
        sa.Column("raw_payload", postgresql.JSONB(), nullable=False),
        sa.Column("asset_count", sa.Integer(), nullable=False),
        sa.Column("software_count", sa.Integer(), nullable=False),
        sa.Column("vulnerability_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_imports_organization_id", "imports", ["organization_id"])

    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("users.id")),
        sa.Column("action", sa.String(128), nullable=False),
        sa.Column("target_type", sa.String(128)),
        sa.Column("target_id", sa.String(128)),
        sa.Column("metadata_json", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_audit_logs_organization_id", "audit_logs", ["organization_id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])


def downgrade() -> None:
    for table in [
        "audit_logs",
        "imports",
        "remediation_tasks",
        "asset_vulnerabilities",
        "software_packages",
        "assets",
        "api_keys",
        "users",
        "cves",
        "organizations",
    ]:
        op.drop_table(table)
# Project version: VulnScope V1.4
