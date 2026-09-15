"""Extracts sampled frames from an uploaded video for inference.

Running inference on every single frame of a video is rarely necessary for
a monitoring use case and is far too slow for a synchronous HTTP request.
Instead, one frame out of every `sample_rate` is processed, which keeps
video inference latency reasonable while still catching sustained safety
violations.
"""

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass
class VideoFrame:
    frame_index: int
    timestamp_seconds: float
    image: np.ndarray


def extract_video_metadata(video_path: str) -> dict:
    capture = cv2.VideoCapture(video_path)
    if not capture.isOpened():
        raise ValueError(f"Could not open video file: {video_path}")

    fps = capture.get(cv2.CAP_PROP_FPS) or 0.0
    frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    capture.release()

    duration_seconds = frame_count / fps if fps > 0 else None
    return {
        "fps": fps,
        "frame_count": frame_count,
        "width": width,
        "height": height,
        "duration_seconds": duration_seconds,
    }


def sample_frames(video_path: str, sample_rate: int) -> list[VideoFrame]:
    """Yield every `sample_rate`-th frame of the video as a VideoFrame."""
    capture = cv2.VideoCapture(video_path)
    if not capture.isOpened():
        raise ValueError(f"Could not open video file: {video_path}")

    fps = capture.get(cv2.CAP_PROP_FPS) or 1.0
    frames = []
    frame_index = 0

    while True:
        success, frame = capture.read()
        if not success:
            break

        if frame_index % sample_rate == 0:
            frames.append(
                VideoFrame(
                    frame_index=frame_index,
                    timestamp_seconds=round(frame_index / fps, 3),
                    image=frame,
                )
            )

        frame_index += 1

    capture.release()
    return frames
