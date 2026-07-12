from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ImportRecord(Base):
    __tablename__ = "imports"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    organization_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("organizations.id"), index=True)
    source: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="processed", nullable=False)
    summary: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    raw_payload: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    asset_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    software_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    vulnerability_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
# Project version: VulnScope V1.5


