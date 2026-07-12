from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.asset import Asset
from app.models.import_record import ImportRecord
from app.models.software_package import SoftwarePackage
from app.models.user import User
from app.schemas.domain import ImportOut, ScanImportIn
from app.services.audit import write_audit

router = APIRouter(prefix="/imports", tags=["imports"])


@router.post("/scan-results", response_model=ImportOut)
def import_scan_results(payload: ScanImportIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    asset_count = 0
    software_count = 0
    for item in payload.assets:
        asset = db.scalar(
            select(Asset).where(
                Asset.organization_id == user.organization_id,
                Asset.hostname == item.hostname,
            )
        )
        asset_data = item.model_dump(exclude={"software"})
        if asset:
            for field, value in asset_data.items():
                setattr(asset, field, value)
        else:
            asset = Asset(organization_id=user.organization_id, **asset_data)
            db.add(asset)
            db.flush()
            asset_count += 1
        for package_item in item.software:
            package = db.scalar(
                select(SoftwarePackage).where(
                    SoftwarePackage.organization_id == user.organization_id,
                    SoftwarePackage.asset_id == asset.id,
                    SoftwarePackage.name == package_item.name,
                    SoftwarePackage.version == package_item.version,
                )
            )
            if not package:
                db.add(SoftwarePackage(organization_id=user.organization_id, asset_id=asset.id, **package_item.model_dump()))
                software_count += 1
    record = ImportRecord(
        organization_id=user.organization_id,
        source=payload.source,
        raw_payload=payload.model_dump(),
        asset_count=asset_count,
        software_count=software_count,
        vulnerability_count=0,
        summary={"assets_created": asset_count, "software_created": software_count},
    )
    db.add(record)
    db.flush()
    write_audit(db, user, "import.scan_results", "import", record.id, record.summary)
    db.commit()
    db.refresh(record)
    return record


@router.get("", response_model=list[ImportOut])
def list_imports(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.scalars(
        select(ImportRecord)
        .where(ImportRecord.organization_id == user.organization_id)
        .order_by(ImportRecord.created_at.desc())
    ).all()
# Project version: VulnScope V1.4
