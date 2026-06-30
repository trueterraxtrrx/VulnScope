from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.asset_vulnerability import AssetVulnerability
from app.models.remediation_task import RemediationTask
from app.models.user import User
from app.schemas.domain import RemediationTaskCreate, RemediationTaskOut, RemediationTaskUpdate
from app.services.audit import write_audit

router = APIRouter(prefix="/remediation-tasks", tags=["remediation"])


@router.get("", response_model=list[RemediationTaskOut])
def list_tasks(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.scalars(
        select(RemediationTask)
        .where(RemediationTask.organization_id == user.organization_id)
        .order_by(RemediationTask.created_at.desc())
    ).all()


@router.post("", response_model=RemediationTaskOut)
def create_task(payload: RemediationTaskCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if payload.asset_vulnerability_id:
        vuln = db.scalar(
            select(AssetVulnerability).where(
                AssetVulnerability.id == payload.asset_vulnerability_id,
                AssetVulnerability.organization_id == user.organization_id,
            )
        )
        if not vuln:
            raise HTTPException(status_code=404, detail="Vulnerability not found")
    task = RemediationTask(organization_id=user.organization_id, **payload.model_dump())
    db.add(task)
    db.flush()
    write_audit(db, user, "remediation.created", "remediation_task", task.id)
    db.commit()
    db.refresh(task)
    return task


@router.patch("/{task_id}", response_model=RemediationTaskOut)
def update_task(task_id: str, payload: RemediationTaskUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    task = db.scalar(select(RemediationTask).where(RemediationTask.id == task_id, RemediationTask.organization_id == user.organization_id))
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    write_audit(db, user, "remediation.updated", "remediation_task", task.id)
    db.commit()
    db.refresh(task)
    return task
# Project version: VulnScope V1.3
