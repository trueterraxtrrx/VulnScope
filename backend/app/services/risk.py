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


def remediation_sla_status(asset: Asset, cve: CVE, age_days: int) -> str:
    cpp_status = _run_cpp_engine("sla", asset.environment, str(asset.criticality), str(cve.cvss_score), str(age_days))
    if cpp_status in {"overdue", "due_soon", "on_track"}:
        return cpp_status
    score = calculate_risk_score(asset, cve)
    limit = 7 if score >= 9.0 else 14 if score >= 7.0 else 30 if score >= 4.0 else 60
    if age_days > limit:
        return "overdue"
    if age_days >= limit - 3:
        return "due_soon"
    return "on_track"


def remediation_priority(asset: Asset, cve: CVE, age_days: int) -> str:
    cpp_priority = _run_cpp_engine("priority", asset.environment, str(asset.criticality), str(cve.cvss_score), str(age_days))
    if cpp_priority in {"p0", "p1", "p2", "p3"}:
        return cpp_priority
    score = calculate_risk_score(asset, cve)
    if score >= 9.0 or age_days > 30:
        return "p0"
    if score >= 7.0 or age_days > 14:
        return "p1"
    if score >= 4.0 or age_days > 7:
        return "p2"
    return "p3"


def summarize_exposure_portfolio(items: list[dict[str, object]]) -> dict[str, object]:
    rows = "\n".join(
        f"{item.get('severity', '')},{float(item.get('risk_score', 0.0))},{item.get('status', '')}"
        for item in items
    )
    cpp_summary = _run_cpp_engine("portfolio", input_text=rows)
    if cpp_summary:
        import json

        try:
            return json.loads(cpp_summary)
        except json.JSONDecodeError:
            pass
    total = len(items)
    open_count = sum(1 for item in items if item.get("status") not in {"fixed", "closed"})
    critical = sum(1 for item in items if item.get("severity") == "critical" or float(item.get("risk_score", 0.0)) >= 9.0)
    urgent = sum(
        1
        for item in items
        if float(item.get("risk_score", 0.0)) >= 7.0 and item.get("status") not in {"fixed", "closed"}
    )
    average = round(sum(float(item.get("risk_score", 0.0)) for item in items) / total, 2) if total else 0.0
    return {"total": total, "open": open_count, "critical": critical, "urgent": urgent, "average_risk": average}


def summarize_sla_backlog(items: list[dict[str, object]]) -> dict[str, int]:
    rows = "\n".join(
        f"{item.get('severity', '')},{float(item.get('risk_score', 0.0))},{item.get('status', '')},{int(item.get('age_days', 0))}"
        for item in items
    )
    cpp_summary = _run_cpp_engine("backlog", input_text=rows)
    if cpp_summary:
        import json

        try:
            parsed = json.loads(cpp_summary)
            if isinstance(parsed, dict):
                return {key: int(parsed.get(key, 0)) for key in ("open_sla_items", "overdue", "due_soon")}
        except json.JSONDecodeError:
            pass
    open_items = [item for item in items if item.get("status") not in {"fixed", "closed"}]
    overdue = sum(1 for item in open_items if int(item.get("age_days", 0)) > 14)
    due_soon = sum(1 for item in open_items if 11 <= int(item.get("age_days", 0)) <= 14)
    return {"open_sla_items": len(open_items), "overdue": overdue, "due_soon": due_soon}


def package_matches_cve(package: SoftwarePackage, cve: CVE) -> bool:
    haystack = f"{cve.title} {cve.description or ''}".lower()
    cpp_match = None
    if os.getenv(CPP_FORCE_ENV) == "1" or len(haystack.encode("utf-8")) >= CPP_MATCH_THRESHOLD_BYTES:
        cpp_match = _run_cpp_engine("match", package.name, input_text=haystack)
    if cpp_match is not None:
        return cpp_match == "1"
    return package.name.lower() in haystack
# Project version: VulnScope V1.5




