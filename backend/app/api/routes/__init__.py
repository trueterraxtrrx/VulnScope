from fastapi import APIRouter

from app.api.routes import api_keys, assets, auth, cves, dashboard, imports, remediation, software, vulnerabilities

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(api_keys.router)
api_router.include_router(assets.router)
api_router.include_router(software.router)
api_router.include_router(cves.router)
api_router.include_router(vulnerabilities.router)
api_router.include_router(remediation.router)
api_router.include_router(imports.router)
api_router.include_router(dashboard.router)
# Project version: VulnScope V1.5
