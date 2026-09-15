"""Wraps the YOLOv8 model used for safety detection inference.

Loading a torch model is expensive, so a single instance is created lazily
and cached for the lifetime of the process through `get_model_service`.
Any class name prefixed with "NO-" (for example "NO-Hardhat") is treated as
a safety violation, matching the label convention of the training dataset
documented in ml/README.md.
"""

from functools import lru_cache
from pathlib import Path

import numpy as np

from app.core.config import get_settings

VIOLATION_PREFIX = "NO-"


class ModelNotFoundError(RuntimeError):
    """Raised when the configured model weights file does not exist."""


class ModelService:
    def __init__(self, model_path: str, confidence_threshold: float, device: str):
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.device = device
        self._model = None
        self._model_version = Path(model_path).stem

    def _ensure_loaded(self) -> None:
        if self._model is not None:
            return

        if not Path(self.model_path).exists():
            raise ModelNotFoundError(
                f"Model weights not found at '{self.model_path}'. Train a model with "
                "ml/src/train.py and export it with ml/src/export_model.py, or set "
                "MODEL_PATH to an existing checkpoint."
            )

        from ultralytics import YOLO  # imported lazily so tests can mock ModelService without torch installed

        self._model = YOLO(self.model_path)

    def predict(self, image: np.ndarray) -> list[dict]:
        """Run inference on a single BGR image array and return raw detections."""
        self._ensure_loaded()

        results = self._model.predict(
            source=image,
            conf=self.confidence_threshold,
            device=self.device,
            verbose=False,
        )

        detections = []
        result = results[0]
        class_names = result.names

        for box in result.boxes:
            class_id = int(box.cls.item())
            class_name = class_names[class_id]
            x_min, y_min, x_max, y_max = [float(v) for v in box.xyxy[0].tolist()]

            detections.append(
                {
                    "class_id": class_id,
                    "class_name": class_name,
                    "confidence": float(box.conf.item()),
                    "bbox_x_min": x_min,
                    "bbox_y_min": y_min,
                    "bbox_x_max": x_max,
                    "bbox_y_max": y_max,
                    "is_violation": class_name.startswith(VIOLATION_PREFIX),
                    "model_name": "yolov8-visionops-ppe",
                    "model_version": self._model_version,
                }
            )

        return detections


@lru_cache
def get_model_service() -> ModelService:
    settings = get_settings()
    return ModelService(
        model_path=settings.model_path,
        confidence_threshold=settings.confidence_threshold,
        device=settings.device,
    )
