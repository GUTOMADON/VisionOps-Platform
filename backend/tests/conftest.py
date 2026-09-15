"""Shared pytest fixtures.

Tests run against an in-memory SQLite database and a fake model service, so
the suite never needs a running Postgres instance, a trained checkpoint, or
torch installed. This keeps CI fast and deterministic while still
exercising the real API and ORM code paths.
"""

import shutil
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db, get_model_service
from app.db.models import Base
from app.main import app


class FakeModelService:
    """Deterministic stand-in for ModelService, avoids loading torch/YOLO in tests."""

    def predict(self, image) -> list[dict]:
        return [
            {
                "class_id": 2,
                "class_name": "NO-Hardhat",
                "confidence": 0.87,
                "bbox_x_min": 10.0,
                "bbox_y_min": 10.0,
                "bbox_x_max": 100.0,
                "bbox_y_max": 100.0,
                "is_violation": True,
                "model_name": "fake-test-model",
                "model_version": "test",
            },
            {
                "class_id": 5,
                "class_name": "Person",
                "confidence": 0.95,
                "bbox_x_min": 5.0,
                "bbox_y_min": 5.0,
                "bbox_x_max": 150.0,
                "bbox_y_max": 200.0,
                "is_violation": False,
                "model_name": "fake-test-model",
                "model_version": "test",
            },
        ]


@pytest.fixture()
def temp_media_dir(monkeypatch):
    media_dir = tempfile.mkdtemp(prefix="visionops_test_media_")
    monkeypatch.setattr("app.services.storage_service.get_settings", lambda: _settings_with_media_dir(media_dir))
    yield media_dir
    shutil.rmtree(media_dir, ignore_errors=True)


def _settings_with_media_dir(media_dir: str):
    from app.core.config import get_settings

    settings = get_settings()
    settings.media_storage_dir = media_dir
    return settings


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session, temp_media_dir):
    def override_get_db():
        yield db_session

    def override_get_model_service():
        return FakeModelService()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_model_service] = override_get_model_service

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
