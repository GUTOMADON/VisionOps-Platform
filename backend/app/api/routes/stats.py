"""Aggregate statistics endpoints backing the dashboard charts."""

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models import Detection, MediaAsset
from app.schemas.detection import ClassSummary, StatsSummaryResponse, StatsTimeseriesResponse, TimeseriesPoint

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/summary", response_model=StatsSummaryResponse)
def get_stats_summary(db: Session = Depends(get_db)) -> StatsSummaryResponse:
    """Overall counts and per class breakdown used by the dashboard's KPI cards."""
    total_media_assets = db.execute(select(func.count()).select_from(MediaAsset)).scalar_one()
    total_detections = db.execute(select(func.count()).select_from(Detection)).scalar_one()
    total_violations = db.execute(
        select(func.count()).select_from(Detection).where(Detection.is_violation.is_(True))
    ).scalar_one()

    if total_detections == 0:
        compliance_rate = 1.0
    else:
        compliance_rate = round((total_detections - total_violations) / total_detections, 4)

    per_class_query = (
        select(
            Detection.class_name,
            func.count().label("total_detections"),
            func.avg(Detection.confidence).label("avg_confidence"),
            func.max(Detection.created_at).label("last_seen_at"),
        )
        .group_by(Detection.class_name)
    )
    per_class_rows = db.execute(per_class_query).all()

    violation_counts = dict(
        db.execute(
            select(Detection.class_name, func.count())
            .where(Detection.is_violation.is_(True))
            .group_by(Detection.class_name)
        ).all()
    )

    by_class = [
        ClassSummary(
            class_name=row.class_name,
            total_detections=row.total_detections,
            total_violations=violation_counts.get(row.class_name, 0),
            avg_confidence=float(row.avg_confidence) if row.avg_confidence is not None else None,
            last_seen_at=row.last_seen_at,
        )
        for row in per_class_rows
    ]

    return StatsSummaryResponse(
        total_media_assets=total_media_assets,
        total_detections=total_detections,
        total_violations=total_violations,
        compliance_rate=compliance_rate,
        by_class=by_class,
    )


@router.get("/timeseries", response_model=StatsTimeseriesResponse)
def get_stats_timeseries(
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    db: Session = Depends(get_db),
) -> StatsTimeseriesResponse:
    """Detection counts bucketed by day, used for the trend chart on the dashboard."""
    query = select(Detection.created_at, Detection.is_violation)
    if start_date is not None:
        query = query.where(Detection.created_at >= start_date)
    if end_date is not None:
        query = query.where(Detection.created_at <= end_date)

    rows = db.execute(query).all()

    buckets: dict[datetime, dict[str, int]] = {}
    for created_at, is_violation in rows:
        bucket_key = created_at.replace(hour=0, minute=0, second=0, microsecond=0)
        bucket = buckets.setdefault(bucket_key, {"total": 0, "violations": 0})
        bucket["total"] += 1
        if is_violation:
            bucket["violations"] += 1

    points = [
        TimeseriesPoint(
            bucket_start=bucket_start,
            total_detections=values["total"],
            total_violations=values["violations"],
        )
        for bucket_start, values in sorted(buckets.items())
    ]

    return StatsTimeseriesResponse(interval="day", points=points)
