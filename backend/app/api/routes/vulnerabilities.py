from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.asset import Asset
from app.models.asset_vulnerability import AssetVulnerability
from app.models.cve import CVE
from app.models.software_package import SoftwarePackage
from app.models.user import User
from app.schemas.domain import MatchRequest, MatchResult, VulnerabilityOut, VulnerabilityStatusUpdate
from app.services.audit import write_audit
from app.services.risk import calculate_risk_score, package_matches_cve

router = APIRouter(prefix="/vulnerabilities", tags=["vulnerabilities"])


@router.get("", response_model=list[VulnerabilityOut])
def list_vulnerabilities(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.scalars(
        select(AssetVulnerability)
        .where(AssetVulnerability.organization_id == user.organization_id)
        .order_by(AssetVulnerability.risk_score.desc())
    ).all()


@router.post("/match", response_model=MatchResult)
def match_vulnerabilities(payload: MatchRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    asset_filter = [SoftwarePackage.asset_id == payload.asset_id] if payload.asset_id else []
    packages = db.scalars(
        select(SoftwarePackage).where(SoftwarePackage.organization_id == user.organization_id, *asset_filter)
    ).all()
    cves = db.scalars(select(CVE)).all()
    created = 0
    for package in packages:
        asset = db.scalar(select(Asset).where(Asset.id == package.asset_id, Asset.organization_id == user.organization_id))
        if not asset:
            continue
        for cve in cves:
            if not package_matches_cve(package, cve):
                continue
            existing = db.scalar(
                select(AssetVulnerability).where(
                    AssetVulnerability.organization_id == user.organization_id,
                    AssetVulnerability.asset_id == asset.id,
                    AssetVulnerability.software_package_id == package.id,
                    AssetVulnerability.cve_id == cve.id,
                )
            )
            if existing:
                continue
            db.add(
                AssetVulnerability(
                    organization_id=user.organization_id,
                    asset_id=asset.id,
                    software_package_id=package.id,
                    cve_id=cve.id,
                    risk_score=calculate_risk_score(asset, cve),
                )
            )
            created += 1
    write_audit(db, user, "vulnerability.match", metadata={"created": created, "asset_id": payload.asset_id})
    db.commit()
    return MatchResult(created=created, message=f"Created {created} vulnerability records")


@router.patch("/{vulnerability_id}/status", response_model=VulnerabilityOut)
def update_status(
    vulnerability_id: str,
    payload: VulnerabilityStatusUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    vuln = db.scalar(
        select(AssetVulnerability).where(
            AssetVulnerability.id == vulnerability_id,
            AssetVulnerability.organization_id == user.organization_id,
        )
    )
    if not vuln:
        raise HTTPException(status_code=404, detail="Vulnerability not found")
    vuln.status = payload.status
    vuln.fixed_at = datetime.utcnow() if payload.status in {"fixed", "accepted", "false_positive"} else None
    write_audit(db, user, "vulnerability.status_updated", "asset_vulnerability", vuln.id, {"status": payload.status})
    db.commit()
    db.refresh(vuln)
    return vuln
# Project version: VulnScope V1.5








