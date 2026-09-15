-- VisionOps Platform - Seed data
-- Provides a small set of realistic rows so the dashboard has content to
-- display immediately after `docker compose up`, before any real media is
-- uploaded through the API. Safe to re-run; it clears prior seed rows first.

DELETE FROM inference_jobs;
DELETE FROM detections;
DELETE FROM media_assets;

-- Two sample media assets, one image and one video, standing in for
-- uploads that would normally be created by the backend during inference.
INSERT INTO media_assets (id, media_type, original_filename, storage_path, content_type, size_bytes, width, height, duration_seconds, uploaded_at)
VALUES
    ('11111111-1111-1111-1111-111111111111', 'image', 'site_entrance_001.jpg', '/data/media/site_entrance_001.jpg', 'image/jpeg', 482311, 1280, 720, NULL, now() - interval '3 hours'),
    ('22222222-2222-2222-2222-222222222222', 'video', 'warehouse_floor_clip.mp4', '/data/media/warehouse_floor_clip.mp4', 'video/mp4', 9821744, 1920, 1080, 12.500, now() - interval '1 hour');

INSERT INTO inference_jobs (id, media_asset_id, status, total_frames, total_detections, total_violations, processing_time_ms, started_at, completed_at)
VALUES
    ('33333333-3333-3333-3333-333333333333', '11111111-1111-1111-1111-111111111111', 'completed', 1, 4, 1, 187, now() - interval '3 hours', now() - interval '3 hours'),
    ('44444444-4444-4444-4444-444444444444', '22222222-2222-2222-2222-222222222222', 'completed', 25, 61, 9, 4032, now() - interval '1 hour', now() - interval '1 hour');

-- Detections for the sample image (one frame, frame_index = 0).
INSERT INTO detections
    (media_asset_id, frame_index, frame_timestamp, class_name, class_id, confidence, bbox_x_min, bbox_y_min, bbox_x_max, bbox_y_max, is_violation, model_name, model_version)
VALUES
    ('11111111-1111-1111-1111-111111111111', 0, 0.0, 'Person',       5, 0.9421, 100.0, 80.0,  340.0, 620.0, false, 'yolov8n-ppe', 'v1.0.0'),
    ('11111111-1111-1111-1111-111111111111', 0, 0.0, 'Hardhat',      0, 0.8877, 130.0, 85.0,  230.0, 160.0, false, 'yolov8n-ppe', 'v1.0.0'),
    ('11111111-1111-1111-1111-111111111111', 0, 0.0, 'Safety Vest',  7, 0.9103, 110.0, 220.0, 320.0, 420.0, false, 'yolov8n-ppe', 'v1.0.0'),
    ('11111111-1111-1111-1111-111111111111', 0, 0.0, 'NO-Mask',      3, 0.7684, 140.0, 90.0,  225.0, 150.0, true,  'yolov8n-ppe', 'v1.0.0');

-- A handful of detections spread across the sample video frames.
INSERT INTO detections
    (media_asset_id, frame_index, frame_timestamp, class_name, class_id, confidence, bbox_x_min, bbox_y_min, bbox_x_max, bbox_y_max, is_violation, model_name, model_version)
VALUES
    ('22222222-2222-2222-2222-222222222222', 0,  0.00, 'Person',        5, 0.9532, 50.0,  40.0,  200.0, 480.0, false, 'yolov8n-ppe', 'v1.0.0'),
    ('22222222-2222-2222-2222-222222222222', 0,  0.00, 'NO-Hardhat',    2, 0.8210, 70.0,  45.0,  160.0, 130.0, true,  'yolov8n-ppe', 'v1.0.0'),
    ('22222222-2222-2222-2222-222222222222', 5,  1.00, 'Person',        5, 0.9301, 300.0, 60.0,  460.0, 500.0, false, 'yolov8n-ppe', 'v1.0.0'),
    ('22222222-2222-2222-2222-222222222222', 5,  1.00, 'Safety Vest',   7, 0.8899, 310.0, 200.0, 450.0, 400.0, false, 'yolov8n-ppe', 'v1.0.0'),
    ('22222222-2222-2222-2222-222222222222', 12, 2.40, 'NO-Safety Vest', 4, 0.7745, 500.0, 90.0,  650.0, 420.0, true,  'yolov8n-ppe', 'v1.0.0'),
    ('22222222-2222-2222-2222-222222222222', 20, 4.00, 'machinery',     8, 0.8560, 700.0, 300.0, 1100.0, 700.0, false, 'yolov8n-ppe', 'v1.0.0');
