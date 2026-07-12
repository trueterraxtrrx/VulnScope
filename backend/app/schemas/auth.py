from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import ORMModel


class RegisterIn(BaseModel):
    organization_name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str | None = None


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class OrganizationOut(ORMModel):
    id: str
    name: str


class UserOut(ORMModel):
    id: str
    organization_id: str
    email: EmailStr
    full_name: str | None
    role: str


class MeOut(UserOut):
    organization: OrganizationOut
# Project version: VulnScope V1.4
