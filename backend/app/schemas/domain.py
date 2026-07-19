from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class AssetBase(BaseModel):
    hostname: str
    ip_address: str | None = None
    os_name: str | None = None
    os_version: str | None = None
    environment: str = "production"
    owner: str | None = None
    criticality: int = Field(default=3, ge=1, le=5)
    last_seen_at: datetime | None = None


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    hostname: str | None = None
    ip_address: str | None = None
    os_name: str | None = None
    os_version: str | None = None
    environment: str | None = None
    owner: str | None = None
    criticality: int | None = Field(default=None, ge=1, le=5)
    last_seen_at: datetime | None = None


class AssetOut(AssetBase, ORMModel):
    id: str
    organization_id: str
    created_at: datetime


class SoftwareBase(BaseModel):
    asset_id: str
    name: str
    version: str
    vendor: str | None = None
    package_type: str = "os"


class SoftwareCreate(SoftwareBase):
    pass


class SoftwareOut(SoftwareBase, ORMModel):
    id: str
    organization_id: str
    created_at: datetime


class CVEBase(BaseModel):
    cve_id: str
    title: str
    description: str | None = None
    severity: str
    cvss_score: float = Field(ge=0, le=10)
    published_at: datetime | None = None
    references: list[str] = []


class CVECreate(CVEBase):
    pass


class CVEOut(CVEBase, ORMModel):
    id: str
    created_at: datetime


class VulnerabilityOut(ORMModel):
    id: str
    organization_id: str
    asset_id: str
    software_package_id: str
    cve_id: str
    status: str
    risk_score: float
    detected_at: datetime
    fixed_at: datetime | None


class VulnerabilityStatusUpdate(BaseModel):
    status: str


class MatchRequest(BaseModel):
    asset_id: str | None = None


class MatchResult(BaseModel):
    created: int
    message: str


class RemediationTaskBase(BaseModel):
    asset_vulnerability_id: str | None = None
    title: str
    description: str | None = None
    status: str = "todo"
    assignee: str | None = None
    due_date: datetime | None = None


class RemediationTaskCreate(RemediationTaskBase):
    pass


class RemediationTaskUpdate(BaseModel):
    asset_vulnerability_id: str | None = None
    title: str | None = None
    description: str | None = None
    status: str | None = None
    assignee: str | None = None
    due_date: datetime | None = None


class RemediationTaskOut(RemediationTaskBase, ORMModel):
    id: str
    organization_id: str
    created_at: datetime


class ScanSoftwareIn(BaseModel):
    name: str
    version: str
    vendor: str | None = None
    package_type: str = "os"


class ScanAssetIn(AssetBase):
    software: list[ScanSoftwareIn] = []


class ScanImportIn(BaseModel):
    source: str = "api"
    assets: list[ScanAssetIn]


class ImportOut(ORMModel):
    id: str
    organization_id: str
    source: str
    status: str
    summary: dict
    asset_count: int
    software_count: int
    vulnerability_count: int
    created_at: datetime


class DashboardStats(BaseModel):
    assets: int
    software_packages: int
    cves: int
    open_vulnerabilities: int
    remediation_tasks: int
    average_risk_score: float
    severity_counts: dict[str, int]
# Project version: VulnScope V1.5







