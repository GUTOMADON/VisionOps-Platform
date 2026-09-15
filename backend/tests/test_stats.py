from app.db.models import Detection, MediaAsset


def _seed_detection(db_session, class_name: str, is_violation: bool) -> None:
    media_asset = MediaAsset(
        media_type="image",
        original_filename="test.jpg",
        storage_path="/tmp/test.jpg",
        content_type="image/jpeg",
    )
    db_session.add(media_asset)
    db_session.flush()

    db_session.add(
        Detection(
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
    )
    db_session.commit()


def test_stats_summary_empty(client):
    response = client.get("/api/v1/stats/summary")
    assert response.status_code == 200
    body = response.json()
    assert body["total_detections"] == 0
    assert body["compliance_rate"] == 1.0
    assert body["by_class"] == []


def test_stats_summary_with_data(client, db_session):
    _seed_detection(db_session, "Hardhat", is_violation=False)
    _seed_detection(db_session, "Hardhat", is_violation=False)
    _seed_detection(db_session, "NO-Hardhat", is_violation=True)

    response = client.get("/api/v1/stats/summary")
    assert response.status_code == 200
    body = response.json()
    assert body["total_detections"] == 3
    assert body["total_violations"] == 1
    assert body["compliance_rate"] == round(2 / 3, 4)

    class_names = {row["class_name"] for row in body["by_class"]}
    assert class_names == {"Hardhat", "NO-Hardhat"}


def test_stats_timeseries_buckets_by_day(client, db_session):
    _seed_detection(db_session, "Hardhat", is_violation=False)

    response = client.get("/api/v1/stats/timeseries")
    assert response.status_code == 200
    body = response.json()
    assert body["interval"] == "day"
    assert len(body["points"]) == 1
    assert body["points"][0]["total_detections"] == 1
