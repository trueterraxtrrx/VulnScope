from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.cve import CVE
from app.models.user import User
from app.schemas.domain import CVECreate, CVEOut
from app.services.audit import write_audit

router = APIRouter(prefix="/cves", tags=["cves"])


@router.get("", response_model=list[CVEOut])
def list_cves(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.scalars(select(CVE).order_by(CVE.published_at.desc().nullslast(), CVE.cve_id)).all()


@router.post("", response_model=CVEOut)
def create_cve(payload: CVECreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    existing = db.scalar(select(CVE).where(CVE.cve_id == payload.cve_id))
    if existing:
        raise HTTPException(status_code=409, detail="CVE already exists")
    cve = CVE(**payload.model_dump())
    db.add(cve)
    db.flush()
    write_audit(db, user, "cve.created", "cve", cve.id)
    db.commit()
    db.refresh(cve)
    return cve


@router.get("/{cve_id}", response_model=CVEOut)
def get_cve(cve_id: str, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    cve = db.scalar(select(CVE).where((CVE.id == cve_id) | (CVE.cve_id == cve_id)))
    if not cve:
        raise HTTPException(status_code=404, detail="CVE not found")
    return cve
# Project version: VulnScope V1.5
