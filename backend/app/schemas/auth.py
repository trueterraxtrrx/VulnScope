from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.common import ORMModel


class RegisterIn(BaseModel):
    organization_name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)
    full_name: str | None = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not any(char.isupper() for char in value):
            raise ValueError("Password must include an uppercase letter")
        if not any(char.islower() for char in value):
            raise ValueError("Password must include a lowercase letter")
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must include a number")
        return value


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
# Project version: VulnScope V1.5





