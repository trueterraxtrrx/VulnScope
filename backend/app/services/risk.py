import os
import subprocess
from pathlib import Path

from app.models.asset import Asset
from app.models.cve import CVE
from app.models.software_package import SoftwarePackage

CPP_RISK_ENGINE_ENV = "VULNSCOPE_CPP_RISK_ENGINE"
CPP_FORCE_ENV = "VULNSCOPE_FORCE_CPP"
CPP_MATCH_THRESHOLD_BYTES = 4096


def _cpp_risk_engine_path() -> Path:
    suffix = ".exe" if os.name == "nt" else ""
    return Path(__file__).resolve().parents[2] / "cpp" / "risk_engine" / f"vulnscope-risk-engine{suffix}"


def _run_cpp_engine(*args: str, input_text: str | None = None) -> str | None:
    configured = os.getenv(CPP_RISK_ENGINE_ENV)
    binary = Path(configured) if configured else _cpp_risk_engine_path()
    if not binary.exists():
        return None
    try:
        completed = subprocess.run(
            [str(binary), *args],
            capture_output=True,
            check=True,
            input=input_text,
            text=True,
            timeout=5,
        )
        return completed.stdout.strip()
    except Exception:
        return None


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
    cpp_score = None
    if os.getenv(CPP_FORCE_ENV) == "1":
        cpp_score = _run_cpp_engine("risk", asset.environment, str(asset.criticality), str(cve.cvss_score))
    if cpp_score is not None:
        return float(cpp_score)
    score = cve.cvss_score * asset_criticality_multiplier(asset) * exposure_multiplier(asset)
    return round(min(score, 10.0), 2)


def package_matches_cve(package: SoftwarePackage, cve: CVE) -> bool:
    haystack = f"{cve.title} {cve.description or ''}".lower()
    cpp_match = None
    if os.getenv(CPP_FORCE_ENV) == "1" or len(haystack.encode("utf-8")) >= CPP_MATCH_THRESHOLD_BYTES:
        cpp_match = _run_cpp_engine("match", package.name, input_text=haystack)
    if cpp_match is not None:
        return cpp_match == "1"
    return package.name.lower() in haystack
# Project version: VulnScope V1.5

