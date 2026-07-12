from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.asset import Asset
from app.models.asset_vulnerability import AssetVulnerability
from app.models.audit_log import AuditLog
from app.models.cve import CVE
from app.models.remediation_task import RemediationTask
from app.models.software_package import SoftwarePackage
from app.models.user import User
from app.schemas.common import AuditLogOut
from app.schemas.domain import DashboardStats

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard/stats", response_model=DashboardStats)
def dashboard_stats(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    org = user.organization_id
    severity_rows = db.execute(
        select(CVE.severity, func.count(AssetVulnerability.id))
        .join(AssetVulnerability, AssetVulnerability.cve_id == CVE.id)
        .where(AssetVulnerability.organization_id == org, AssetVulnerability.status == "open")
        .group_by(CVE.severity)
    ).all()
    avg_risk = db.scalar(
        select(func.coalesce(func.avg(AssetVulnerability.risk_score), 0)).where(
            AssetVulnerability.organization_id == org,
            AssetVulnerability.status == "open",
        )
    )
    return DashboardStats(
        assets=db.scalar(select(func.count(Asset.id)).where(Asset.organization_id == org)) or 0,
        software_packages=db.scalar(select(func.count(SoftwarePackage.id)).where(SoftwarePackage.organization_id == org)) or 0,
        cves=db.scalar(select(func.count(CVE.id))) or 0,
        open_vulnerabilities=db.scalar(
            select(func.count(AssetVulnerability.id)).where(
                AssetVulnerability.organization_id == org,
                AssetVulnerability.status == "open",
            )
        )
        or 0,
        remediation_tasks=db.scalar(select(func.count(RemediationTask.id)).where(RemediationTask.organization_id == org)) or 0,
        average_risk_score=round(float(avg_risk or 0), 2),
        severity_counts={severity: count for severity, count in severity_rows},
    )


@router.get("/audit-logs", response_model=list[AuditLogOut])
def audit_logs(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.scalars(
        select(AuditLog)
        .where(AuditLog.organization_id == user.organization_id)
        .order_by(AuditLog.created_at.desc())
        .limit(200)
    ).all()
# Project version: VulnScope V1.5



