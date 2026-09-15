"""Pydantic schemas for request validation and API responses."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BoundingBox(BaseModel):
    x_min: float
    y_min: float
    x_max: float
    y_max: float


class DetectionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    media_asset_id: str
    frame_index: int
    frame_timestamp: float | None
    class_name: str
    class_id: int
    confidence: float
    bbox_x_min: float
    bbox_y_min: float
    bbox_x_max: float
    bbox_y_max: float
    is_violation: bool
    model_name: str
    model_version: str
    created_at: datetime


class DetectionListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[DetectionOut]


class MediaAssetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    media_type: str
    original_filename: str
    content_type: str | None
    size_bytes: int | None
    width: int | None
    height: int | None
    duration_seconds: float | None
    uploaded_at: datetime


class InferenceResponse(BaseModel):
    job_id: str
    media_asset: MediaAssetOut
    status: str
    total_frames: int
    total_detections: int
    total_violations: int
    processing_time_ms: int
    detections: list[DetectionOut]


class ClassSummary(BaseModel):
    class_name: str
    total_detections: int
    total_violations: int
    avg_confidence: float | None
    last_seen_at: datetime | None


class StatsSummaryResponse(BaseModel):
    total_media_assets: int
    total_detections: int
    total_violations: int
    compliance_rate: float = Field(..., description="Share of detections that are not a violation, between 0 and 1.")
    by_class: list[ClassSummary]


class TimeseriesPoint(BaseModel):
    bucket_start: datetime
    total_detections: int
    total_violations: int


class StatsTimeseriesResponse(BaseModel):
    interval: str
    points: list[TimeseriesPoint]


class ErrorResponse(BaseModel):
    detail: str
