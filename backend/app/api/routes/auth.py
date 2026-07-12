from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.organization import Organization
from app.models.user import User
from app.schemas.auth import LoginIn, MeOut, RegisterIn
from app.schemas.common import Token

router = APIRouter(tags=["auth"])


@router.post("/auth/register", response_model=Token)
def register(payload: RegisterIn, db: Session = Depends(get_db)) -> Token:
    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    org = Organization(name=payload.organization_name)
    db.add(org)
    db.flush()
    user = User(
        organization_id=org.id,
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        role="admin",
    )
    db.add(user)
    db.commit()
    return Token(access_token=create_access_token(user.id))


@router.post("/auth/login", response_model=Token)
def login(payload: LoginIn, db: Session = Depends(get_db)) -> Token:
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return Token(access_token=create_access_token(user.id))


@router.get("/me", response_model=MeOut)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
# Project version: VulnScope V1.5

