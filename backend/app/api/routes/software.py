from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.asset import Asset
from app.models.software_package import SoftwarePackage
from app.models.user import User
from app.schemas.domain import SoftwareCreate, SoftwareOut
from app.services.audit import write_audit

router = APIRouter(prefix="/software", tags=["software"])


@router.get("", response_model=list[SoftwareOut])
def list_software(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.scalars(select(SoftwarePackage).where(SoftwarePackage.organization_id == user.organization_id).order_by(SoftwarePackage.name)).all()


@router.post("", response_model=SoftwareOut)
def create_software(payload: SoftwareCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    asset = db.scalar(select(Asset).where(Asset.id == payload.asset_id, Asset.organization_id == user.organization_id))
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    package = SoftwarePackage(organization_id=user.organization_id, **payload.model_dump())
    db.add(package)
    db.flush()
    write_audit(db, user, "software.created", "software_package", package.id)
    db.commit()
    db.refresh(package)
    return package
# Project version: VulnScope V1.5


