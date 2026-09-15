"""Liveness and readiness endpoints used by Docker health checks and load balancers."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import get_db

router = APIRouter(tags=["health"])


@router.get("/health", summary="Liveness check")
def health() -> dict:
    return {"status": "ok"}


@router.get("/health/ready", summary="Readiness check, verifies the database is reachable")
def readiness(db: Session = Depends(get_db)) -> dict:
    db.execute(text("SELECT 1"))
    return {"status": "ready"}
