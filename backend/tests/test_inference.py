import cv2
import numpy as np


def _make_jpeg_bytes() -> bytes:
    image = np.zeros((64, 64, 3), dtype=np.uint8)
    success, encoded = cv2.imencode(".jpg", image)
    assert success
    return encoded.tobytes()


def test_infer_image_success(client):
    jpeg_bytes = _make_jpeg_bytes()

    response = client.post(
        "/api/v1/inference/image",
        files={"file": ("sample.jpg", jpeg_bytes, "image/jpeg")},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["total_detections"] == 2
    assert body["total_violations"] == 1
    assert body["media_asset"]["media_type"] == "image"
    assert len(body["detections"]) == 2
    assert any(detection["class_name"] == "NO-Hardhat" for detection in body["detections"])


def test_infer_image_rejects_wrong_content_type(client):
    response = client.post(
        "/api/v1/inference/image",
        files={"file": ("sample.txt", b"not an image", "text/plain")},
    )
    assert response.status_code == 415
    assert "detail" in response.json()


def test_infer_image_rejects_empty_file(client):
    response = client.post(
        "/api/v1/inference/image",
        files={"file": ("sample.jpg", b"", "image/jpeg")},
    )
    assert response.status_code == 400


def test_infer_video_rejects_wrong_content_type(client):
    response = client.post(
        "/api/v1/inference/video",
        files={"file": ("sample.jpg", b"not a video", "image/jpeg")},
    )
    assert response.status_code == 415
