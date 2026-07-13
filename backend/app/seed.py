from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.asset import Asset
from app.models.cve import CVE
from app.models.organization import Organization
from app.models.software_package import SoftwarePackage
from app.models.user import User


def run() -> None:
    db = SessionLocal()
    try:
        if db.scalar(select(User).where(User.email == "admin@krynex.local")):
            return
        org = Organization(name="KRYNEX Demo")
        db.add(org)
        db.flush()
        user = User(
            organization_id=org.id,
            email="admin@krynex.local",
            full_name="Security Admin",
            hashed_password=hash_password("password123"),
            role="admin",
        )
        asset = Asset(
            organization_id=org.id,
            hostname="web-01",
            ip_address="10.0.0.10",
            os_name="Ubuntu",
            os_version="24.04",
            environment="production",
            owner="platform",
            criticality=4,
        )
        db.add_all([user, asset])
        db.flush()
        db.add(SoftwarePackage(organization_id=org.id, asset_id=asset.id, name="openssl", version="3.0.13", vendor="OpenSSL", package_type="deb"))
        db.add(
            CVE(
                cve_id="CVE-2026-0001",
                title="OpenSSL package vulnerability",
                description="Demo defensive-only CVE record matching installed openssl packages.",
                severity="high",
                cvss_score=8.1,
                references=[],
            )
        )
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    run()
# Project version: VulnScope V1.5




