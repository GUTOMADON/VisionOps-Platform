"""Inference endpoints: run the safety detection model on an uploaded image
or video and persist every detection to the database.
"""

import time

import cv2
import numpy as np
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_model_service
from app.core.config import get_settings
from app.db.models import Detection, InferenceJob, MediaAsset
from app.schemas.detection import InferenceResponse
from app.services.model_service import ModelNotFoundError, ModelService
from app.services.storage_service import get_media_type, save_upload
from app.services.video_service import extract_video_metadata, sample_frames

router = APIRouter(prefix="/inference", tags=["inference"])


def _validate_upload(upload: UploadFile, contents: bytes, expected_media_type: str) -> None:
    settings = get_settings()

    media_type = get_media_type(upload.content_type)
    if media_type != expected_media_type:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported content type '{upload.content_type}' for {expected_media_type} inference.",
        )

    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds the maximum allowed size of {settings.max_upload_size_mb} MB.",
        )

    if len(contents) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty.")


def _run_model_safely(model_service: ModelService, image: np.ndarray) -> list[dict]:
    try:
        return model_service.predict(image)
    except ModelNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.post("/image", response_model=InferenceResponse, status_code=status.HTTP_201_CREATED)
async def infer_image(
    file: UploadFile,
    db: Session = Depends(get_db),
    model_service: ModelService = Depends(get_model_service),
) -> InferenceResponse:
    """Run detection on a single image and store every detected object."""
    contents = await file.read()
    _validate_upload(file, contents, expected_media_type="image")

    image_array = cv2.imdecode(np.frombuffer(contents, dtype=np.uint8), cv2.IMREAD_COLOR)
    if image_array is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not decode image file.")

    storage_path = save_upload(file, contents)
    height, width = image_array.shape[:2]

    media_asset = MediaAsset(
        media_type="image",
        original_filename=file.filename or "upload.jpg",
        storage_path=storage_path,
        content_type=file.content_type,
        size_bytes=len(contents),
        width=width,
        height=height,
    )
    db.add(media_asset)
    db.flush()

    start_time = time.perf_counter()
    raw_detections = _run_model_safely(model_service, image_array)
    processing_time_ms = int((time.perf_counter() - start_time) * 1000)

    detections = [
        Detection(media_asset_id=media_asset.id, frame_index=0, frame_timestamp=0.0, **raw)
        for raw in raw_detections
    ]
    db.add_all(detections)

    job = InferenceJob(
        media_asset_id=media_asset.id,
        status="completed",
        total_frames=1,
        total_detections=len(detections),
        total_violations=sum(1 for d in detections if d.is_violation),
        processing_time_ms=processing_time_ms,
    )
    db.add(job)
    db.commit()

    db.refresh(media_asset)
    for detection in detections:
        db.refresh(detection)

    return InferenceResponse(
        job_id=job.id,
        media_asset=media_asset,
        status=job.status,
        total_frames=job.total_frames,
        total_detections=job.total_detections,
        total_violations=job.total_violations,
        processing_time_ms=job.processing_time_ms,
        detections=detections,
    )


@router.post("/video", response_model=InferenceResponse, status_code=status.HTTP_201_CREATED)
async def infer_video(
    file: UploadFile,
    db: Session = Depends(get_db),
    model_service: ModelService = Depends(get_model_service),
) -> InferenceResponse:
    """Run detection on a sampled set of frames from an uploaded video."""
    settings = get_settings()
    contents = await file.read()
    _validate_upload(file, contents, expected_media_type="video")

    storage_path = save_upload(file, contents)

    try:
        metadata = extract_video_metadata(storage_path)
        frames = sample_frames(storage_path, sample_rate=settings.video_frame_sample_rate)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    media_asset = MediaAsset(
        media_type="video",
        original_filename=file.filename or "upload.mp4",
        storage_path=storage_path,
        content_type=file.content_type,
        size_bytes=len(contents),
        width=metadata["width"],
        height=metadata["height"],
        duration_seconds=metadata["duration_seconds"],
    )
    db.add(media_asset)
    db.flush()

    start_time = time.perf_counter()
    all_detections = []
    for frame in frames:
        raw_detections = _run_model_safely(model_service, frame.image)
        for raw in raw_detections:
            all_detections.append(
                Detection(
                    media_asset_id=media_asset.id,
                    frame_index=frame.frame_index,
                    frame_timestamp=frame.timestamp_seconds,
                    **raw,
                )
            )
    processing_time_ms = int((time.perf_counter() - start_time) * 1000)

    db.add_all(all_detections)

    job = InferenceJob(
        media_asset_id=media_asset.id,
        status="completed",
        total_frames=len(frames),
        total_detections=len(all_detections),
        total_violations=sum(1 for d in all_detections if d.is_violation),
        processing_time_ms=processing_time_ms,
    )
    db.add(job)
    db.commit()

    db.refresh(media_asset)
    for detection in all_detections:
        db.refresh(detection)

    return InferenceResponse(
        job_id=job.id,
        media_asset=media_asset,
        status=job.status,
        total_frames=job.total_frames,
        total_detections=job.total_detections,
        total_violations=job.total_violations,
        processing_time_ms=job.processing_time_ms,
        detections=all_detections,
    )
