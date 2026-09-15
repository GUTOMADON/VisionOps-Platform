"""Endpoints for browsing stored detections, backing the dashboard's history table."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models import Detection
from app.schemas.detection import DetectionListResponse, DetectionOut

router = APIRouter(prefix="/detections", tags=["detections"])


@router.get("", response_model=DetectionListResponse)
def list_detections(
    class_name: str | None = Query(None, description="Filter by exact class name, for example 'NO-Hardhat'."),
    is_violation: bool | None = Query(None, description="Filter to only violations or only compliant detections."),
    media_asset_id: str | None = Query(None, description="Filter to detections from a single media asset."),
    start_date: datetime | None = Query(None, description="Only include detections created on or after this time."),
    end_date: datetime | None = Query(None, description="Only include detections created on or before this time."),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> DetectionListResponse:
    """List detections with optional filters, newest first."""
    query = select(Detection)

    if class_name is not None:
        query = query.where(Detection.class_name == class_name)
    if is_violation is not None:
        query = query.where(Detection.is_violation == is_violation)
    if media_asset_id is not None:
        query = query.where(Detection.media_asset_id == media_asset_id)
    if start_date is not None:
        query = query.where(Detection.created_at >= start_date)
    if end_date is not None:
        query = query.where(Detection.created_at <= end_date)

    total = db.execute(select(func.count()).select_from(query.subquery())).scalar_one()

    query = query.order_by(Detection.created_at.desc()).limit(limit).offset(offset)
    items = db.execute(query).scalars().all()

    return DetectionListResponse(total=total, limit=limit, offset=offset, items=items)


@router.get("/{detection_id}", response_model=DetectionOut)
def get_detection(detection_id: str, db: Session = Depends(get_db)) -> DetectionOut:
    """Fetch a single detection by id."""
    detection = db.get(Detection, detection_id)
    if detection is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Detection '{detection_id}' not found.")
    return detection
