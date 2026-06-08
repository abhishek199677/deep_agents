from __future__ import annotations

from fastapi import APIRouter

from agentic.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.app_env,
        "version": "1.0.0",
    }


@router.get("/ready")
async def readiness():
    """Readiness probe — used by load balancers / Kubernetes."""
    return {"status": "ready"}
