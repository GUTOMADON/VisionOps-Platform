"""SQLAlchemy ORM models mirroring database/init.sql.

Kept as the single source of truth for the Python side of the schema. The
raw SQL in database/init.sql is what actually provisions the production
database (so the schema is reviewable independently of the ORM), and
`Base.metadata.create_all` is used only for local development and tests.
"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.db.types import GUID, new_uuid


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class MediaAsset(Base):
    __tablename__ = "media_assets"

    id: Mapped[str] = mapped_column(GUID, primary_key=True, default=new_uuid)
    media_type: Mapped[str] = mapped_column(String(10), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    content_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration_seconds: Mapped[float | None] = mapped_column(Numeric(10, 3), nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(default=utcnow)

    detections: Mapped[list["Detection"]] = relationship(
        back_populates="media_asset", cascade="all, delete-orphan"
    )
    inference_jobs: Mapped[list["InferenceJob"]] = relationship(
        back_populates="media_asset", cascade="all, delete-orphan"
    )


class Detection(Base):
    __tablename__ = "detections"

    id: Mapped[str] = mapped_column(GUID, primary_key=True, default=new_uuid)
    media_asset_id: Mapped[str] = mapped_column(GUID, ForeignKey("media_assets.id", ondelete="CASCADE"), nullable=False)
    frame_index: Mapped[int] = mapped_column(Integer, default=0)
    frame_timestamp: Mapped[float | None] = mapped_column(Numeric(10, 3), nullable=True)
    class_name: Mapped[str] = mapped_column(String(100), nullable=False)
    class_id: Mapped[int] = mapped_column(Integer, nullable=False)
    confidence: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)
    bbox_x_min: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False)
    bbox_y_min: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False)
    bbox_x_max: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False)
    bbox_y_max: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False)
    is_violation: Mapped[bool] = mapped_column(Boolean, default=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    media_asset: Mapped["MediaAsset"] = relationship(back_populates="detections")


class InferenceJob(Base):
    __tablename__ = "inference_jobs"

    id: Mapped[str] = mapped_column(GUID, primary_key=True, default=new_uuid)
    media_asset_id: Mapped[str] = mapped_column(GUID, ForeignKey("media_assets.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="completed")
    total_frames: Mapped[int] = mapped_column(Integer, default=1)
    total_detections: Mapped[int] = mapped_column(Integer, default=0)
    total_violations: Mapped[int] = mapped_column(Integer, default=0)
    processing_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)

    media_asset: Mapped["MediaAsset"] = relationship(back_populates="inference_jobs")
