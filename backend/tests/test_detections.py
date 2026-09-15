from app.db.models import Detection, MediaAsset


def _seed_detection(db_session, class_name: str, is_violation: bool) -> Detection:
    media_asset = MediaAsset(
        media_type="image",
        original_filename="test.jpg",
        storage_path="/tmp/test.jpg",
        content_type="image/jpeg",
        size_bytes=1024,
        width=640,
        height=480,
    )
    db_session.add(media_asset)
    db_session.flush()

    detection = Detection(
        media_asset_id=media_asset.id,
        frame_index=0,
        frame_timestamp=0.0,
        class_name=class_name,
        class_id=1,
        confidence=0.9,
        bbox_x_min=0.0,
        bbox_y_min=0.0,
        bbox_x_max=10.0,
        bbox_y_max=10.0,
        is_violation=is_violation,
        model_name="test-model",
        model_version="v0",
    )
    db_session.add(detection)
    db_session.commit()
    return detection


def test_list_detections_empty(client):
    response = client.get("/api/v1/detections")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 0
    assert body["items"] == []


def test_list_detections_returns_seeded_rows(client, db_session):
    _seed_detection(db_session, "Hardhat", is_violation=False)
    _seed_detection(db_session, "NO-Hardhat", is_violation=True)

    response = client.get("/api/v1/detections")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert len(body["items"]) == 2


def test_list_detections_filters_by_violation(client, db_session):
    _seed_detection(db_session, "Hardhat", is_violation=False)
    _seed_detection(db_session, "NO-Hardhat", is_violation=True)

    response = client.get("/api/v1/detections", params={"is_violation": True})
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["class_name"] == "NO-Hardhat"


def test_list_detections_pagination(client, db_session):
    for i in range(5):
        _seed_detection(db_session, f"class_{i}", is_violation=False)

    response = client.get("/api/v1/detections", params={"limit": 2, "offset": 1})
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 5
    assert len(body["items"]) == 2


def test_get_detection_by_id(client, db_session):
    detection = _seed_detection(db_session, "Safety Vest", is_violation=False)

    response = client.get(f"/api/v1/detections/{detection.id}")
    assert response.status_code == 200
    assert response.json()["id"] == detection.id


def test_get_detection_not_found(client):
    response = client.get("/api/v1/detections/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
