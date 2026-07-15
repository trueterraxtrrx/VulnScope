from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class Message(BaseModel):
    message: str


class AuditLogOut(ORMModel):
    id: str
    organization_id: str
    user_id: str | None
    action: str
    target_type: str | None
    target_id: str | None
    metadata_json: dict
    created_at: datetime
# Project version: VulnScope V1.5





