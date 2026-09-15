"""Shared FastAPI dependencies re-exported for convenience in route modules."""

from app.db.session import get_db
from app.services.model_service import ModelService, get_model_service

__all__ = ["get_db", "get_model_service", "ModelService"]
