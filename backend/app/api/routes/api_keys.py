import secrets
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import hash_password
from app.db.session import get_db
from app.models.user import APIKey, User
from app.schemas.common import ORMModel
from app.services.audit import write_audit

router = APIRouter(prefix="/api-keys", tags=["api-keys"])


class APIKeyCreate(ORMModel):
    name: str


class APIKeyOut(ORMModel):
    id: str
    name: str
    key_prefix: str
    created_at: datetime
    last_used_at: datetime | None


class APIKeyCreated(APIKeyOut):
    token: str


@router.get("", response_model=list[APIKeyOut])
def list_api_keys(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.scalars(select(APIKey).where(APIKey.organization_id == user.organization_id).order_by(APIKey.created_at.desc())).all()


@router.post("", response_model=APIKeyCreated)
def create_api_key(payload: APIKeyCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    token = f"vscope_{secrets.token_urlsafe(32)}"
    key = APIKey(
        organization_id=user.organization_id,
        user_id=user.id,
        name=payload.name,
        key_prefix=token[:14],
        hashed_key=hash_password(token),
    )
    db.add(key)
    db.flush()
    write_audit(db, user, "api_key.created", "api_key", key.id, {"name": payload.name})
    db.commit()
    db.refresh(key)
    return APIKeyCreated.model_validate(key).model_copy(update={"token": token})


@router.delete("/{api_key_id}", status_code=204)
def delete_api_key(api_key_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    key = db.scalar(select(APIKey).where(APIKey.id == api_key_id, APIKey.organization_id == user.organization_id))
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    db.delete(key)
    write_audit(db, user, "api_key.deleted", "api_key", api_key_id)
    db.commit()
# Project version: VulnScope V1.5



