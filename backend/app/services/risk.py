from app.models.asset import Asset
from app.models.cve import CVE
from app.models.software_package import SoftwarePackage


def exposure_multiplier(asset: Asset) -> float:
    if asset.environment == "internet":
        return 1.5
    if asset.environment == "production":
        return 1.25
    if asset.environment == "staging":
        return 1.0
    return 0.8


def asset_criticality_multiplier(asset: Asset) -> float:
    return {1: 0.7, 2: 0.9, 3: 1.0, 4: 1.25, 5: 1.5}.get(asset.criticality, 1.0)


def calculate_risk_score(asset: Asset, cve: CVE) -> float:
    score = cve.cvss_score * asset_criticality_multiplier(asset) * exposure_multiplier(asset)
    return round(min(score, 10.0), 2)


def package_matches_cve(package: SoftwarePackage, cve: CVE) -> bool:
    haystack = f"{cve.title} {cve.description or ''}".lower()
    return package.name.lower() in haystack
# Project version: VulnScope V1.4
