from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.asset import Asset
from app.models.user import User
from app.schemas.domain import AssetCreate, AssetOut, AssetUpdate
from app.services.audit import write_audit

router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("", response_model=list[AssetOut])
def list_assets(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.scalars(select(Asset).where(Asset.organization_id == user.organization_id).order_by(Asset.hostname)).all()


@router.post("", response_model=AssetOut)
def create_asset(payload: AssetCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    asset = Asset(organization_id=user.organization_id, **payload.model_dump())
    db.add(asset)
    db.flush()
    write_audit(db, user, "asset.created", "asset", asset.id)
    db.commit()
    db.refresh(asset)
    return asset


@router.get("/{asset_id}", response_model=AssetOut)
def get_asset(asset_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    asset = db.scalar(select(Asset).where(Asset.id == asset_id, Asset.organization_id == user.organization_id))
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@router.patch("/{asset_id}", response_model=AssetOut)
def update_asset(asset_id: str, payload: AssetUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    asset = db.scalar(select(Asset).where(Asset.id == asset_id, Asset.organization_id == user.organization_id))
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(asset, field, value)
    write_audit(db, user, "asset.updated", "asset", asset.id)
    db.commit()
    db.refresh(asset)
    return asset
# Project version: VulnScope V1.3
